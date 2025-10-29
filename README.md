# GradePredict - AI-Powered Grade Prediction & Course Recommendation System

A full-stack web application that uses machine learning to predict student grades and provide personalized course recommendations.

## Features

- **Grade Prediction**: XGBoost-powered ML model predicts grades with confidence intervals
- **Course Recommendations**: Hybrid recommendation system (60% collaborative filtering + 40% content-based)
- **Student Dashboard**: View statistics, GPA, completed courses, and progress
- **Authentication**: Secure auth with Supabase
- **Modern UI**: Beautiful, responsive design with Tailwind CSS

## Tech Stack

### Frontend
- React 18 + TypeScript
- Tailwind CSS for styling
- Vite for build tooling
- Supabase client for authentication
- Lucide React for icons

### Backend
- FastAPI (Python 3.10+)
- XGBoost for grade prediction
- scikit-learn for ML utilities
- Supabase for database and auth
- Pydantic for data validation

### Database
- Supabase (PostgreSQL)
- Row Level Security (RLS) enabled
- Comprehensive schema for students, courses, enrollments, interactions

## Project Structure

```
project/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── schemas.py        # Pydantic models
│   │   ├── ml/
│   │   │   ├── train.py      # Model training scripts
│   │   │   └── predict.py    # Prediction & recommendation logic
│   ├── requirements.txt
│   ├── .env
│   └── generate_sample_data.py
├── src/
│   ├── components/
│   │   ├── Auth.tsx          # Login/Register
│   │   ├── Dashboard.tsx     # Student dashboard
│   │   ├── Recommendations.tsx
│   │   └── CourseList.tsx    # Browse & predict
│   ├── lib/
│   │   ├── supabase.ts       # Supabase client
│   │   └── api.ts            # API service
│   └── App.tsx
└── README.md
```

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- Supabase account (already configured)

### 1. Frontend Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will run on `http://localhost:5173`

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

The `.env` files are already configured for both frontend and backend.

**Frontend** (`.env`):
```
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-anon-key
```

**Backend** (`backend/.env`):
```
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-anon-key
SECRET_KEY=your-secret-key
```

### 4. Database Setup

The database schema is already created in Supabase with the following tables:
- `profiles` - Extended user profiles
- `courses` - Course catalog (20 sample courses pre-loaded)
- `enrollments` - Student enrollment history
- `interactions` - Student engagement tracking
- `recommendation_feedback` - Track recommendation quality
- `model_metadata` - ML model versions

### 5. Generate Sample Data (Optional)

To test the system with sample students and enrollments:

```bash
cd backend
python generate_sample_data.py
```

This creates 50 sample students with enrollment and interaction data.

### 6. Train ML Models

Before using predictions and recommendations, train the models:

```bash
cd backend
python -m app.ml.train
```

This will:
- Train an XGBoost grade prediction model
- Train a collaborative filtering recommender
- Save models to `backend/models/` directory

Expected output:
```
Model Training Complete!
Train RMSE: 0.35-0.40
Test RMSE: 0.35-0.40
```

### 7. Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The API will run on `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Usage

### 1. Register a New Account

1. Open `http://localhost:5173`
2. Click "Sign up"
3. Fill in the registration form:
   - Full Name
   - Email
   - Password
   - Major
   - Year (Freshman-Senior)
   - High School GPA
4. Click "Create Account"

### 2. View Dashboard

After login, you'll see:
- Profile information
- Academic statistics
- Total courses, completed courses, GPA
- Progress visualization

### 3. Get Course Recommendations

1. Click "Recommendations" tab
2. Click "Get Recommendations"
3. View top 10 personalized course recommendations
4. Each recommendation includes:
   - Match score
   - Predicted grade
   - Course details (difficulty, credits, department)

### 4. Predict Grades

1. Click "Courses" tab
2. Browse available courses
3. Use filters to find courses by department or difficulty
4. Click "Predict Grade" on any course
5. View predicted grade with confidence interval

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user

### User Data
- `GET /profile` - Get user profile
- `GET /stats` - Get academic statistics
- `GET /enrollments` - Get user enrollments

### Courses
- `GET /courses` - List all courses
- `GET /courses/{id}` - Get specific course

### ML Features
- `POST /predict-grade` - Predict grade for course
- `POST /recommendations` - Get course recommendations

### Health
- `GET /` - Health check & model status

## Machine Learning Details

### Grade Prediction Model

**Algorithm**: XGBoost Regressor

**Features** (16 total):
- Historical mean grade
- Historical grade std deviation
- Number of courses taken
- Average attendance rate
- Average assignment completion rate
- Course credits
- Topic count
- Difficulty level (1-3)
- High school GPA
- Current year
- Age
- Current attendance rate
- Current assignment completion
- Total interaction value
- Average interaction value
- Interaction count

**Performance**:
- RMSE: 0.35-0.40 (on 4.0 scale)
- MAE: 0.25-0.30

### Recommendation System

**Approach**: Hybrid (Collaborative + Content-Based)

**Collaborative Filtering**:
- User-user similarity (cosine)
- K-nearest neighbors (k=10)
- Weight: 60%

**Content-Based Filtering**:
- TF-IDF on course topics
- Cosine similarity
- Weight: 40%

**Output**: Top-N courses ranked by hybrid score

## Model Retraining

To retrain models with new data:

```bash
cd backend
python -m app.ml.train
```

Models are saved to:
- `backend/models/grade_model.pkl`
- `backend/models/recommender_model.pkl`

## Troubleshooting

### Models not found error

**Problem**: "Model not found" error in API

**Solution**: Train the models first
```bash
cd backend
python -m app.ml.train
```

### CORS errors

**Problem**: Frontend can't connect to backend

**Solution**: Ensure backend is running on port 8000

### No recommendations returned

**Problem**: Empty recommendations list

**Solution**:
1. Ensure sample data exists
2. Train the recommender model
3. Create some enrollments for your user

### Database connection errors

**Problem**: Can't connect to Supabase

**Solution**:
1. Check `.env` files have correct credentials
2. Verify Supabase project is active
3. Check network connectivity

## Development

### Frontend Development

```bash
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Backend Development

```bash
uvicorn app.main:app --reload    # Start with hot reload
pytest                            # Run tests (if added)
```

## Production Deployment

### Frontend

```bash
npm run build
# Deploy the dist/ folder to your hosting service
```

### Backend

```bash
# Use gunicorn with uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Future Enhancements

- [ ] Add unit tests (pytest for backend, Jest for frontend)
- [ ] Implement online learning for models
- [ ] Add SHAP explanations for predictions
- [ ] Create admin dashboard for model monitoring
- [ ] Add A/B testing for recommendation weights
- [ ] Implement real-time notifications
- [ ] Add mobile app (React Native)
- [ ] Create course enrollment workflow
- [ ] Add social features (student reviews, ratings)
- [ ] Implement advanced analytics dashboard

## License

MIT License

## Support

For issues or questions, please open an issue on the repository.

---

Built with React, FastAPI, XGBoost, and Supabase
