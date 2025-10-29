export const API_BASE_URL = "https://grade-prediction-5b5n.onrender.com";


export interface PredictGradeResponse {
  student_id: string;
  course_id: string;
  predicted_grade: number;
  confidence_interval: number;
  grade_range: {
    lower: number;
    upper: number;
  };
  letter_grade: string;
}

export interface CourseRecommendation {
  course_id: string;
  course_code: string;
  course_title: string;
  score: number;
  predicted_grade: number | null;
  department: string;
  credits: number;
  difficulty: string;
}

export interface RecommendationResponse {
  student_id: string;
  recommendations: CourseRecommendation[];
  generated_at: string;
}

export interface Stats {
  total_courses: number;
  completed_courses: number;
  in_progress_courses: number;
  average_grade: number;
  total_credits: number;
  current_gpa: number;
}

export class ApiService {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  async predictGrade(studentId: string, courseId: string): Promise<PredictGradeResponse> {
    const response = await fetch(`${API_BASE_URL}/predict-grade`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        student_id: studentId,
        course_id: courseId,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to predict grade');
    }

    return response.json();
  }

  async getRecommendations(studentId: string, n: number = 10): Promise<RecommendationResponse> {
    const response = await fetch(`${API_BASE_URL}/recommendations`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        student_id: studentId,
        n,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get recommendations');
    }

    return response.json();
  }

  async getStats(): Promise<Stats> {
    const response = await fetch(`${API_BASE_URL}/stats`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get stats');
    }

    return response.json();
  }

  async getCourses() {
    const response = await fetch(`${API_BASE_URL}/courses`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get courses');
    }

    return response.json();
  }

  async getProfile() {
    const response = await fetch(`${API_BASE_URL}/profile`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get profile');
    }

    return response.json();
  }
}

export const apiService = new ApiService();
