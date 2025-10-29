import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import xgboost as xgb
import joblib
from datetime import datetime
import json
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

class GradePredictionTrainer:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []

    def fetch_data_from_supabase(self):
        """Fetch training data from Supabase"""
        supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )

        enrollments = supabase.table('enrollments').select('*').execute()
        profiles = supabase.table('profiles').select('*').execute()
        courses = supabase.table('courses').select('*').execute()
        interactions = supabase.table('interactions').select('*').execute()

        enrollments_df = pd.DataFrame(enrollments.data)
        profiles_df = pd.DataFrame(profiles.data)
        courses_df = pd.DataFrame(courses.data)
        interactions_df = pd.DataFrame(interactions.data)

        return enrollments_df, profiles_df, courses_df, interactions_df

    def engineer_features(self, enrollments_df, profiles_df, courses_df, interactions_df):
        """Create features for grade prediction"""

        if len(enrollments_df) == 0:
            print("No enrollment data available for training")
            return None, None

        student_history = enrollments_df[enrollments_df['status'] == 'completed'].groupby('student_id').agg({
            'grade': ['mean', 'std', 'count'],
            'attendance_rate': 'mean',
            'assignment_completion_rate': 'mean'
        }).reset_index()

        student_history.columns = [
            'student_id', 'hist_mean_grade', 'hist_std_grade',
            'hist_course_count', 'hist_avg_attendance', 'hist_avg_completion'
        ]

        student_history['hist_std_grade'] = student_history['hist_std_grade'].fillna(0)

        interaction_stats = interactions_df.groupby('student_id').agg({
            'value': ['sum', 'mean', 'count']
        }).reset_index()

        if len(interaction_stats) > 0:
            interaction_stats.columns = ['student_id', 'total_interaction_value', 'avg_interaction_value', 'interaction_count']
        else:
            interaction_stats = pd.DataFrame(columns=['student_id', 'total_interaction_value', 'avg_interaction_value', 'interaction_count'])

        df = enrollments_df[enrollments_df['status'] == 'completed'].copy()
        df = df.merge(student_history, on='student_id', how='left')
        df = df.merge(profiles_df, left_on='student_id', right_on='id', how='left')
        df = df.merge(courses_df, left_on='course_id', right_on='id', how='left', suffixes=('', '_course'))
        df = df.merge(interaction_stats, on='student_id', how='left')

        df['topic_count'] = df['topics'].apply(lambda x: len(x) if isinstance(x, list) else 0)

        difficulty_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
        df['difficulty_num'] = df['difficulty'].map(difficulty_map).fillna(2)

        features = [
            'hist_mean_grade', 'hist_std_grade', 'hist_course_count',
            'hist_avg_attendance', 'hist_avg_completion',
            'credits', 'topic_count', 'difficulty_num',
            'high_school_gpa', 'year', 'age',
            'attendance_rate', 'assignment_completion_rate',
            'total_interaction_value', 'avg_interaction_value', 'interaction_count'
        ]

        df = df.dropna(subset=['grade'])

        for feat in features:
            if feat not in df.columns:
                df[feat] = 0

        X = df[features].fillna(0)
        y = df['grade']

        self.feature_names = features

        return X, y

    def train(self, X, y):
        """Train the XGBoost model"""

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        self.model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )

        self.model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_test_scaled, y_test)],
            verbose=False
        )

        train_preds = self.model.predict(X_train_scaled)
        test_preds = self.model.predict(X_test_scaled)

        train_rmse = np.sqrt(mean_squared_error(y_train, train_preds))
        test_rmse = np.sqrt(mean_squared_error(y_test, test_preds))
        train_mae = mean_absolute_error(y_train, train_preds)
        test_mae = mean_absolute_error(y_test, test_preds)

        metrics = {
            'train_rmse': float(train_rmse),
            'test_rmse': float(test_rmse),
            'train_mae': float(train_mae),
            'test_mae': float(test_mae),
            'n_samples': len(X),
            'n_features': len(self.feature_names)
        }

        print(f"\nModel Training Complete!")
        print(f"Train RMSE: {train_rmse:.4f}")
        print(f"Test RMSE: {test_rmse:.4f}")
        print(f"Train MAE: {train_mae:.4f}")
        print(f"Test MAE: {test_mae:.4f}")

        return metrics

    def save_model(self, path='models/grade_model.pkl'):
        """Save the trained model"""
        os.makedirs(os.path.dirname(path), exist_ok=True)

        model_artifact = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'trained_at': datetime.now().isoformat()
        }

        joblib.dump(model_artifact, path)
        print(f"Model saved to {path}")

        return model_artifact


class RecommenderTrainer:
    def __init__(self):
        self.user_item_matrix = None
        self.user_similarity = None
        self.course_features = None

    def fetch_data_from_supabase(self):
        """Fetch data for recommender training"""
        supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )

        enrollments = supabase.table('enrollments').select('*').execute()
        courses = supabase.table('courses').select('*').execute()

        enrollments_df = pd.DataFrame(enrollments.data)
        courses_df = pd.DataFrame(courses.data)

        return enrollments_df, courses_df

    def build_user_item_matrix(self, enrollments_df):
        """Build user-item interaction matrix"""

        ratings_df = enrollments_df[enrollments_df['status'] == 'completed'][
            ['student_id', 'course_id', 'grade']
        ].copy()

        ratings_df['grade'] = ratings_df['grade'].fillna(2.0)

        user_item_matrix = ratings_df.pivot_table(
            index='student_id',
            columns='course_id',
            values='grade',
            fill_value=0
        )

        return user_item_matrix

    def compute_user_similarity(self, user_item_matrix):
        """Compute user-user similarity using cosine similarity"""
        from sklearn.metrics.pairwise import cosine_similarity

        similarity_matrix = cosine_similarity(user_item_matrix)

        similarity_df = pd.DataFrame(
            similarity_matrix,
            index=user_item_matrix.index,
            columns=user_item_matrix.index
        )

        return similarity_df

    def extract_course_features(self, courses_df):
        """Extract TF-IDF features from course topics"""
        from sklearn.feature_extraction.text import TfidfVectorizer

        courses_df['topics_str'] = courses_df['topics'].apply(
            lambda x: ' '.join(x) if isinstance(x, list) else ''
        )

        vectorizer = TfidfVectorizer(max_features=50)
        topic_features = vectorizer.fit_transform(courses_df['topics_str'])

        course_features = {
            'course_ids': courses_df['id'].tolist(),
            'features': topic_features,
            'vectorizer': vectorizer
        }

        return course_features

    def train(self, enrollments_df, courses_df):
        """Train the recommender system"""

        if len(enrollments_df) == 0:
            print("No enrollment data available for training recommender")
            return {}

        self.user_item_matrix = self.build_user_item_matrix(enrollments_df)
        self.user_similarity = self.compute_user_similarity(self.user_item_matrix)
        self.course_features = self.extract_course_features(courses_df)

        metrics = {
            'n_users': len(self.user_item_matrix),
            'n_courses': len(self.user_item_matrix.columns),
            'sparsity': 1 - (self.user_item_matrix != 0).sum().sum() / (self.user_item_matrix.shape[0] * self.user_item_matrix.shape[1])
        }

        print(f"\nRecommender Training Complete!")
        print(f"Users: {metrics['n_users']}")
        print(f"Courses: {metrics['n_courses']}")
        print(f"Sparsity: {metrics['sparsity']:.2%}")

        return metrics

    def save_model(self, path='models/recommender_model.pkl'):
        """Save the trained recommender"""
        os.makedirs(os.path.dirname(path), exist_ok=True)

        recommender_artifact = {
            'user_item_matrix': self.user_item_matrix,
            'user_similarity': self.user_similarity,
            'course_features': self.course_features,
            'trained_at': datetime.now().isoformat()
        }

        joblib.dump(recommender_artifact, path)
        print(f"Recommender saved to {path}")

        return recommender_artifact


def main():
    """Main training pipeline"""
    print("=" * 60)
    print("Grade Prediction & Recommendation System - Model Training")
    print("=" * 60)

    print("\n1. Training Grade Prediction Model...")
    grade_trainer = GradePredictionTrainer()

    enrollments_df, profiles_df, courses_df, interactions_df = grade_trainer.fetch_data_from_supabase()

    X, y = grade_trainer.engineer_features(enrollments_df, profiles_df, courses_df, interactions_df)

    if X is not None and len(X) > 0:
        grade_metrics = grade_trainer.train(X, y)
        grade_trainer.save_model()
    else:
        print("Insufficient data for grade prediction training")
        grade_metrics = {}

    print("\n2. Training Recommender System...")
    recommender_trainer = RecommenderTrainer()

    enrollments_df, courses_df = recommender_trainer.fetch_data_from_supabase()

    if len(enrollments_df) > 0:
        recommender_metrics = recommender_trainer.train(enrollments_df, courses_df)
        recommender_trainer.save_model()
    else:
        print("Insufficient data for recommender training")
        recommender_metrics = {}

    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
