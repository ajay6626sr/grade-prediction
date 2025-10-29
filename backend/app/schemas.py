from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    major: Optional[str] = ""
    year: Optional[int] = Field(1, ge=1, le=4)
    high_school_gpa: Optional[float] = Field(0.0, ge=0.0, le=4.0)
    age: Optional[int] = Field(18, ge=16, le=100)
    gender: Optional[str] = ""


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str


class Profile(BaseModel):
    id: str
    full_name: str
    major: str
    year: int
    high_school_gpa: float
    age: Optional[int]
    gender: str
    created_at: datetime


class Course(BaseModel):
    id: str
    code: str
    title: str
    description: str
    credits: int
    difficulty: str
    topics: List[str]
    department: str


class EnrollmentCreate(BaseModel):
    course_id: str
    semester: str
    year: int
    attendance_rate: Optional[float] = 0.0
    assignment_completion_rate: Optional[float] = 0.0


class Enrollment(BaseModel):
    id: str
    student_id: str
    course_id: str
    semester: str
    year: int
    grade: Optional[float]
    letter_grade: Optional[str]
    status: str
    attendance_rate: float
    assignment_completion_rate: float


class PredictGradeRequest(BaseModel):
    student_id: str
    course_id: str


class PredictGradeResponse(BaseModel):
    student_id: str
    course_id: str
    predicted_grade: float
    confidence_interval: float
    grade_range: Dict[str, float]
    letter_grade: str


class RecommendationRequest(BaseModel):
    student_id: str
    n: Optional[int] = 10


class CourseRecommendation(BaseModel):
    course_id: str
    course_code: str
    course_title: str
    score: float
    predicted_grade: Optional[float]
    department: str
    credits: int
    difficulty: str


class RecommendationResponse(BaseModel):
    student_id: str
    recommendations: List[CourseRecommendation]
    generated_at: datetime


class InteractionCreate(BaseModel):
    course_id: str
    event_type: str
    value: float


class StatsResponse(BaseModel):
    total_courses: int
    completed_courses: int
    in_progress_courses: int
    average_grade: float
    total_credits: int
    current_gpa: float


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    models_loaded: Dict[str, bool]
