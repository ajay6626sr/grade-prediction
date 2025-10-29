import numpy as np
import pandas as pd
import joblib
import os
from typing import Dict, List, Tuple
from sklearn.metrics.pairwise import cosine_similarity


class GradePredictor:
    def __init__(self, model_path='models/grade_model.pkl'):
        """Load the trained grade prediction model"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Please train the model first.")

        artifact = joblib.load(model_path)
        self.model = artifact['model']
        self.scaler = artifact['scaler']
        self.feature_names = artifact['feature_names']

    def predict(self, features: Dict) -> Tuple[float, float]:
        """
        Predict grade for a student-course pair

        Args:
            features: Dictionary containing all required features

        Returns:
            Tuple of (predicted_grade, confidence_interval)
        """
        feature_values = []
        for feat_name in self.feature_names:
            feature_values.append(features.get(feat_name, 0))

        X = np.array([feature_values])
        X_scaled = self.scaler.transform(X)

        pred = self.model.predict(X_scaled)[0]

        pred = np.clip(pred, 0.0, 4.0)

        if hasattr(self.model, 'predict') and hasattr(self.model, 'get_booster'):
            leaf_preds = []
            for tree_idx in range(min(10, self.model.n_estimators)):
                tree_pred = self.model.predict(X_scaled)
                leaf_preds.append(tree_pred[0])

            std_dev = np.std(leaf_preds) if len(leaf_preds) > 1 else 0.2
        else:
            std_dev = 0.2

        confidence_interval = 1.96 * std_dev

        return float(pred), float(confidence_interval)

    def predict_batch(self, features_list: List[Dict]) -> List[Tuple[float, float]]:
        """Predict grades for multiple student-course pairs"""
        predictions = []

        for features in features_list:
            pred, ci = self.predict(features)
            predictions.append((pred, ci))

        return predictions


class CourseRecommender:
    def __init__(self, model_path='models/recommender_model.pkl'):
        """Load the trained recommender model"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Recommender model not found at {model_path}. Please train the model first.")

        artifact = joblib.load(model_path)
        self.user_item_matrix = artifact['user_item_matrix']
        self.user_similarity = artifact['user_similarity']
        self.course_features = artifact['course_features']

    def get_collaborative_scores(self, student_id: str, k: int = 10) -> Dict[str, float]:
        """
        Get collaborative filtering scores for all courses

        Args:
            student_id: The student's ID
            k: Number of similar users to consider

        Returns:
            Dictionary mapping course_id to predicted score
        """
        if student_id not in self.user_item_matrix.index:
            return {}

        similar_users = self.user_similarity[student_id].nlargest(k + 1).index[1:]

        scores = {}
        for course_id in self.user_item_matrix.columns:
            if self.user_item_matrix.loc[student_id, course_id] > 0:
                continue

            similar_user_ratings = []
            similarities = []

            for similar_user in similar_users:
                rating = self.user_item_matrix.loc[similar_user, course_id]
                if rating > 0:
                    similar_user_ratings.append(rating)
                    similarities.append(self.user_similarity.loc[student_id, similar_user])

            if similar_user_ratings:
                weighted_sum = sum(r * s for r, s in zip(similar_user_ratings, similarities))
                similarity_sum = sum(similarities)
                scores[course_id] = weighted_sum / similarity_sum if similarity_sum > 0 else 0
            else:
                scores[course_id] = 0

        return scores

    def get_content_based_scores(self, student_id: str, enrolled_courses: List[str]) -> Dict[str, float]:
        """
        Get content-based filtering scores

        Args:
            student_id: The student's ID
            enrolled_courses: List of course IDs the student has completed

        Returns:
            Dictionary mapping course_id to similarity score
        """
        if not enrolled_courses:
            return {course_id: 0.5 for course_id in self.course_features['course_ids']}

        enrolled_indices = [
            i for i, cid in enumerate(self.course_features['course_ids'])
            if cid in enrolled_courses
        ]

        if not enrolled_indices:
            return {course_id: 0.5 for course_id in self.course_features['course_ids']}

        enrolled_features = self.course_features['features'][enrolled_indices]
        avg_student_profile = enrolled_features.mean(axis=0)

        similarities = cosine_similarity(
            avg_student_profile.reshape(1, -1),
            self.course_features['features']
        )[0]

        scores = {}
        for i, course_id in enumerate(self.course_features['course_ids']):
            if course_id not in enrolled_courses:
                scores[course_id] = float(similarities[i])

        return scores

    def recommend(
        self,
        student_id: str,
        enrolled_courses: List[str],
        n: int = 10,
        cf_weight: float = 0.6,
        cb_weight: float = 0.4
    ) -> List[Tuple[str, float]]:
        """
        Generate hybrid recommendations

        Args:
            student_id: The student's ID
            enrolled_courses: List of course IDs the student has completed
            n: Number of recommendations to return
            cf_weight: Weight for collaborative filtering
            cb_weight: Weight for content-based filtering

        Returns:
            List of (course_id, score) tuples
        """
        cf_scores = self.get_collaborative_scores(student_id)
        cb_scores = self.get_content_based_scores(student_id, enrolled_courses)

        all_courses = set(cf_scores.keys()) | set(cb_scores.keys())

        hybrid_scores = {}
        for course_id in all_courses:
            cf_score = cf_scores.get(course_id, 0)
            cb_score = cb_scores.get(course_id, 0)

            cf_score_norm = (cf_score / 4.0) if cf_score > 0 else 0
            cb_score_norm = cb_score

            hybrid_score = cf_weight * cf_score_norm + cb_weight * cb_score_norm
            hybrid_scores[course_id] = hybrid_score

        sorted_recommendations = sorted(
            hybrid_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_recommendations[:n]

    def get_popular_courses(self, n: int = 10) -> List[str]:
        """Get most popular courses based on enrollment count"""
        course_popularity = (self.user_item_matrix > 0).sum(axis=0)
        popular_courses = course_popularity.nlargest(n).index.tolist()
        return popular_courses


def load_models(grade_model_path='models/grade_model.pkl', recommender_path='models/recommender_model.pkl'):
    """Convenience function to load both models"""
    try:
        grade_predictor = GradePredictor(grade_model_path)
    except FileNotFoundError:
        grade_predictor = None
        print(f"Warning: Grade prediction model not found at {grade_model_path}")

    try:
        recommender = CourseRecommender(recommender_path)
    except FileNotFoundError:
        recommender = None
        print(f"Warning: Recommender model not found at {recommender_path}")

    return grade_predictor, recommender
