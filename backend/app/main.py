from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional, List
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import pandas as pd

from app.schemas import (
    UserCreate, UserLogin, Token, Profile, Course,
    EnrollmentCreate, Enrollment, PredictGradeRequest,
    PredictGradeResponse, RecommendationRequest, RecommendationResponse,
    CourseRecommendation, InteractionCreate, StatsResponse, HealthResponse
)
from app.ml.predict import GradePredictor, CourseRecommender

load_dotenv()

app = FastAPI(
    title="Grade Prediction & Course Recommendation API",
    description="ML-powered grade prediction and course recommendation system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

security = HTTPBearer()

grade_predictor: Optional[GradePredictor] = None
recommender: Optional[CourseRecommender] = None

try:
    grade_predictor = GradePredictor()
    print("✓ Grade prediction model loaded successfully")
except Exception as e:
    print(f"✗ Grade prediction model not loaded: {e}")

try:
    recommender = CourseRecommender()
    print("✓ Recommender model loaded successfully")
except Exception as e:
    print(f"✗ Recommender model not loaded: {e}")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token and return user ID"""
    try:
        token = credentials.credentials
        user = supabase.auth.get_user(token)
        if user and user.user:
            return user.user.id
        raise HTTPException(status_code=401, detail="Invalid authentication")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication")


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        models_loaded={
            "grade_predictor": grade_predictor is not None,
            "recommender": recommender is not None
        }
    )


@app.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password
        })

        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Registration failed")

        user_id = auth_response.user.id

        profile_data = {
            "id": user_id,
            "full_name": user_data.full_name,
            "major": user_data.major or "",
            "year": user_data.year,
            "high_school_gpa": user_data.high_school_gpa,
            "age": user_data.age,
            "gender": user_data.gender or ""
        }

        supabase.table('profiles').insert(profile_data).execute()

        return Token(
            access_token=auth_response.session.access_token,
            token_type="bearer",
            user_id=user_id,
            email=user_data.email
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login user"""
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })

        if not auth_response.user or not auth_response.session:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return Token(
            access_token=auth_response.session.access_token,
            token_type="bearer",
            user_id=auth_response.user.id,
            email=auth_response.user.email
        )

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/profile", response_model=Profile)
async def get_profile(user_id: str = Depends(get_current_user)):
    """Get user profile"""
    try:
        response = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=404, detail="Profile not found")


@app.get("/courses", response_model=List[Course])
async def get_courses(user_id: str = Depends(get_current_user)):
    """Get all available courses"""
    try:
        response = supabase.table('courses').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: str, user_id: str = Depends(get_current_user)):
    """Get a specific course"""
    try:
        response = supabase.table('courses').select('*').eq('id', course_id).single().execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=404, detail="Course not found")


@app.get("/enrollments", response_model=List[Enrollment])
async def get_enrollments(user_id: str = Depends(get_current_user)):
    """Get user's enrollments"""
    try:
        response = supabase.table('enrollments').select('*').eq('student_id', user_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/enrollments", response_model=Enrollment)
async def create_enrollment(enrollment: EnrollmentCreate, user_id: str = Depends(get_current_user)):
    """Create a new enrollment"""
    try:
        enrollment_data = {
            "student_id": user_id,
            "course_id": enrollment.course_id,
            "semester": enrollment.semester,
            "year": enrollment.year,
            "status": "in_progress",
            "attendance_rate": enrollment.attendance_rate,
            "assignment_completion_rate": enrollment.assignment_completion_rate
        }

        response = supabase.table('enrollments').insert(enrollment_data).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/interactions")
async def create_interaction(interaction: InteractionCreate, user_id: str = Depends(get_current_user)):
    """Log a student interaction"""
    try:
        interaction_data = {
            "student_id": user_id,
            "course_id": interaction.course_id,
            "event_type": interaction.event_type,
            "value": interaction.value
        }

        supabase.table('interactions').insert(interaction_data).execute()
        return {"message": "Interaction logged successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/stats", response_model=StatsResponse)
async def get_stats(user_id: str = Depends(get_current_user)):
    """Get user statistics"""
    try:
        enrollments_response = supabase.table('enrollments').select('*').eq('student_id', user_id).execute()
        enrollments = enrollments_response.data

        if not enrollments:
            return StatsResponse(
                total_courses=0,
                completed_courses=0,
                in_progress_courses=0,
                average_grade=0.0,
                total_credits=0,
                current_gpa=0.0
            )

        completed = [e for e in enrollments if e['status'] == 'completed']
        in_progress = [e for e in enrollments if e['status'] == 'in_progress']

        grades = [e['grade'] for e in completed if e['grade'] is not None]
        avg_grade = sum(grades) / len(grades) if grades else 0.0

        course_ids = list(set([e['course_id'] for e in enrollments]))
        courses_response = supabase.table('courses').select('credits').in_('id', course_ids).execute()
        total_credits = sum([c['credits'] for c in courses_response.data])

        return StatsResponse(
            total_courses=len(enrollments),
            completed_courses=len(completed),
            in_progress_courses=len(in_progress),
            average_grade=round(avg_grade, 2),
            total_credits=total_credits,
            current_gpa=round(avg_grade, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict-grade", response_model=PredictGradeResponse)
async def predict_grade(request: PredictGradeRequest, user_id: str = Depends(get_current_user)):
    """Predict grade for a student-course pair"""
    if not grade_predictor:
        raise HTTPException(status_code=503, detail="Grade prediction model not available")

    try:
        if request.student_id != user_id:
            raise HTTPException(status_code=403, detail="Cannot predict grades for other users")

        profile_response = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        profile = profile_response.data

        enrollments_response = supabase.table('enrollments').select('*').eq('student_id', user_id).eq('status', 'completed').execute()
        enrollments = enrollments_response.data

        course_response = supabase.table('courses').select('*').eq('id', request.course_id).single().execute()
        course = course_response.data

        interactions_response = supabase.table('interactions').select('*').eq('student_id', user_id).execute()
        interactions = interactions_response.data

        completed_grades = [e['grade'] for e in enrollments if e['grade'] is not None]
        hist_mean_grade = sum(completed_grades) / len(completed_grades) if completed_grades else 0.0
        hist_std_grade = pd.Series(completed_grades).std() if len(completed_grades) > 1 else 0.0
        hist_course_count = len(enrollments)

        attendance_rates = [e['attendance_rate'] for e in enrollments if e['attendance_rate'] is not None]
        hist_avg_attendance = sum(attendance_rates) / len(attendance_rates) if attendance_rates else 0.0

        completion_rates = [e['assignment_completion_rate'] for e in enrollments if e['assignment_completion_rate'] is not None]
        hist_avg_completion = sum(completion_rates) / len(completion_rates) if completion_rates else 0.0

        interaction_values = [i['value'] for i in interactions]
        total_interaction_value = sum(interaction_values)
        avg_interaction_value = sum(interaction_values) / len(interaction_values) if interaction_values else 0.0
        interaction_count = len(interactions)

        difficulty_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
        difficulty_num = difficulty_map.get(course['difficulty'], 2)

        features = {
            'hist_mean_grade': hist_mean_grade,
            'hist_std_grade': hist_std_grade,
            'hist_course_count': hist_course_count,
            'hist_avg_attendance': hist_avg_attendance,
            'hist_avg_completion': hist_avg_completion,
            'credits': course['credits'],
            'topic_count': len(course['topics']) if course['topics'] else 0,
            'difficulty_num': difficulty_num,
            'high_school_gpa': profile['high_school_gpa'],
            'year': profile['year'],
            'age': profile['age'] if profile['age'] else 20,
            'attendance_rate': 85.0,
            'assignment_completion_rate': 90.0,
            'total_interaction_value': total_interaction_value,
            'avg_interaction_value': avg_interaction_value,
            'interaction_count': interaction_count
        }

        predicted_grade, confidence_interval = grade_predictor.predict(features)

        lower_bound = max(0.0, predicted_grade - confidence_interval)
        upper_bound = min(4.0, predicted_grade + confidence_interval)

        def grade_to_letter(grade: float) -> str:
            if grade >= 3.7:
                return "A"
            elif grade >= 3.3:
                return "A-"
            elif grade >= 3.0:
                return "B+"
            elif grade >= 2.7:
                return "B"
            elif grade >= 2.3:
                return "B-"
            elif grade >= 2.0:
                return "C+"
            elif grade >= 1.7:
                return "C"
            elif grade >= 1.3:
                return "C-"
            elif grade >= 1.0:
                return "D"
            else:
                return "F"

        return PredictGradeResponse(
            student_id=user_id,
            course_id=request.course_id,
            predicted_grade=round(predicted_grade, 2),
            confidence_interval=round(confidence_interval, 2),
            grade_range={
                "lower": round(lower_bound, 2),
                "upper": round(upper_bound, 2)
            },
            letter_grade=grade_to_letter(predicted_grade)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest, user_id: str = Depends(get_current_user)):
    """Get course recommendations for a student"""
    if not recommender:
        raise HTTPException(status_code=503, detail="Recommender model not available")

    try:
        if request.student_id != user_id:
            raise HTTPException(status_code=403, detail="Cannot get recommendations for other users")

        enrollments_response = supabase.table('enrollments').select('course_id').eq('student_id', user_id).execute()
        enrolled_course_ids = [e['course_id'] for e in enrollments_response.data]

        recommendations = recommender.recommend(
            student_id=user_id,
            enrolled_courses=enrolled_course_ids,
            n=request.n
        )

        if not recommendations:
            popular_courses = recommender.get_popular_courses(n=request.n)
            recommendations = [(cid, 0.5) for cid in popular_courses if cid not in enrolled_course_ids]

        course_ids = [rec[0] for rec in recommendations]
        courses_response = supabase.table('courses').select('*').in_('id', course_ids).execute()
        courses_dict = {c['id']: c for c in courses_response.data}

        course_recommendations = []
        for course_id, score in recommendations:
            if course_id in courses_dict:
                course = courses_dict[course_id]

                predicted_grade = None
                if grade_predictor:
                    try:
                        profile_response = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
                        profile = profile_response.data

                        enrollments_completed = supabase.table('enrollments').select('*').eq('student_id', user_id).eq('status', 'completed').execute()
                        completed_enrollments = enrollments_completed.data

                        completed_grades = [e['grade'] for e in completed_enrollments if e['grade'] is not None]
                        hist_mean_grade = sum(completed_grades) / len(completed_grades) if completed_grades else 0.0

                        difficulty_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
                        features = {
                            'hist_mean_grade': hist_mean_grade,
                            'hist_std_grade': 0.0,
                            'hist_course_count': len(completed_enrollments),
                            'hist_avg_attendance': 85.0,
                            'hist_avg_completion': 90.0,
                            'credits': course['credits'],
                            'topic_count': len(course['topics']) if course['topics'] else 0,
                            'difficulty_num': difficulty_map.get(course['difficulty'], 2),
                            'high_school_gpa': profile['high_school_gpa'],
                            'year': profile['year'],
                            'age': profile['age'] if profile['age'] else 20,
                            'attendance_rate': 85.0,
                            'assignment_completion_rate': 90.0,
                            'total_interaction_value': 0.0,
                            'avg_interaction_value': 0.0,
                            'interaction_count': 0
                        }
                        pred, _ = grade_predictor.predict(features)
                        predicted_grade = round(pred, 2)
                    except:
                        pass

                course_recommendations.append(CourseRecommendation(
                    course_id=course_id,
                    course_code=course['code'],
                    course_title=course['title'],
                    score=round(score, 3),
                    predicted_grade=predicted_grade,
                    department=course['department'],
                    credits=course['credits'],
                    difficulty=course['difficulty']
                ))

        return RecommendationResponse(
            student_id=user_id,
            recommendations=course_recommendations,
            generated_at=datetime.now()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
