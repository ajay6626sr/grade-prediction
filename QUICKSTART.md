# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Start Frontend (Terminal 1)

```bash
# Already in project root
npm run dev
```

Open `http://localhost:5173`

### Step 2: Setup Backend (Terminal 2)

```bash
cd backend

# Create & activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Generate Sample Data

```bash
# Still in backend directory
python generate_sample_data.py
```

This creates 50 students with realistic enrollment data.

### Step 4: Train ML Models

```bash
# Still in backend directory
python -m app.ml.train
```

Expected output:
```
Model Training Complete!
Train RMSE: 0.35-0.40
Test RMSE: 0.35-0.40
Recommender Training Complete!
```

### Step 5: Start Backend Server

```bash
# Still in backend directory
uvicorn app.main:app --reload --port 8000
```

API running at `http://localhost:8000`
Docs at `http://localhost:8000/docs`

### Step 6: Use the Application

1. Open `http://localhost:5173`
2. Click "Sign up" and create an account
3. Fill in your profile information
4. Explore the Dashboard
5. Go to "Recommendations" and click "Get Recommendations"
6. Go to "Courses" and click "Predict Grade" on any course

## 🎯 Test with Sample Data

### Login as Sample Student

If you ran the sample data generator, you can login with:

- Email: `student1@example.com` to `student50@example.com`
- Password: `password123`

These accounts have historical enrollment data for better predictions.

## 🔧 Troubleshooting

### Issue: Models not found

```bash
cd backend
python -m app.ml.train
```

### Issue: No courses showing

The database should have 20 courses pre-loaded. Check:
```bash
# In backend directory with venv activated
python
>>> from supabase import create_client
>>> import os
>>> from dotenv import load_dotenv
>>> load_dotenv()
>>> supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
>>> courses = supabase.table('courses').select('*').execute()
>>> print(len(courses.data))
```

Should return 20.

### Issue: CORS errors

Ensure backend is running on port 8000 and frontend on 5173.

## 📊 What to Try

1. **Dashboard**: View your academic statistics
2. **Recommendations**: Get AI-powered course suggestions with predicted grades
3. **Courses**: Browse all courses and predict your grade in each one
4. **Filters**: Use department and difficulty filters in the course list

## 🎓 Sample Workflow

1. Register a new student account
2. View your empty dashboard
3. Go to "Courses" and explore the catalog
4. Click "Predict Grade" on 5-10 courses
5. Go to "Recommendations" and get personalized suggestions
6. Compare the predicted grades between random courses and recommended courses
   (Recommended courses should have higher predicted grades!)

## 📚 Learn More

- Read `README.md` for full documentation
- Check API docs at `http://localhost:8000/docs`
- Explore the ML models in `backend/app/ml/`

## 🐛 Common Issues

**Backend won't start**: Make sure virtual environment is activated and all dependencies installed

**Frontend errors**: Run `npm install` again

**No predictions**: Train the models first with `python -m app.ml.train`

**Empty recommendations**: Generate sample data or create some enrollments manually

---

Enjoy exploring GradePredict! 🎉
