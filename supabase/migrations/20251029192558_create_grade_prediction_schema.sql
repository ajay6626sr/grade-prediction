/*
  # Grade Prediction & Course Recommendation System - Database Schema

  ## Overview
  Complete database schema for a full-stack grade prediction and course recommendation system.
  
  ## Tables Created
  
  1. **profiles** - Extended user profiles beyond auth.users
     - `id` (uuid, references auth.users)
     - `full_name` (text)
     - `major` (text)
     - `year` (integer) - academic year (1-4)
     - `high_school_gpa` (numeric)
     - `age` (integer)
     - `gender` (text)
     - `created_at`, `updated_at` (timestamptz)
  
  2. **courses** - Available courses
     - `id` (uuid, primary key)
     - `code` (text, unique) - e.g., CS101
     - `title` (text)
     - `description` (text)
     - `credits` (integer)
     - `difficulty` (text) - Beginner, Intermediate, Advanced
     - `topics` (text[]) - array of topic keywords
     - `department` (text)
     - `created_at` (timestamptz)
  
  3. **enrollments** - Student enrollment history
     - `id` (uuid, primary key)
     - `student_id` (uuid, references profiles)
     - `course_id` (uuid, references courses)
     - `semester` (text) - Fall, Spring, Summer
     - `year` (integer)
     - `grade` (numeric) - 0.0 to 4.0 GPA scale
     - `letter_grade` (text) - A, B+, B, etc.
     - `status` (text) - completed, in_progress, dropped
     - `attendance_rate` (numeric) - percentage
     - `assignment_completion_rate` (numeric) - percentage
     - `created_at`, `updated_at` (timestamptz)
  
  4. **interactions** - Student engagement tracking
     - `id` (uuid, primary key)
     - `student_id` (uuid, references profiles)
     - `course_id` (uuid, references courses)
     - `event_type` (text) - video_watch, forum_post, assignment_submit, quiz_attempt
     - `value` (numeric) - duration in minutes, count, score
     - `timestamp` (timestamptz)
  
  5. **recommendation_feedback** - Track recommendation quality
     - `id` (uuid, primary key)
     - `student_id` (uuid, references profiles)
     - `course_id` (uuid, references courses)
     - `recommended_at` (timestamptz)
     - `clicked` (boolean) - did user click on recommendation
     - `enrolled` (boolean) - did user enroll
     - `outcome_grade` (numeric) - actual grade if enrolled
     - `feedback_rating` (integer) - 1-5 star rating
     - `created_at` (timestamptz)
  
  6. **model_metadata** - Track ML model versions and performance
     - `id` (uuid, primary key)
     - `model_type` (text) - grade_predictor, recommender
     - `version` (text)
     - `metrics` (jsonb) - RMSE, MAE, Precision@K, etc.
     - `trained_at` (timestamptz)
     - `is_active` (boolean)
  
  ## Security
  - Enable RLS on all tables
  - Users can only access their own data
  - Authenticated users can read courses
  - Only authenticated users can create enrollments and interactions
*/

-- Create profiles table
CREATE TABLE IF NOT EXISTS profiles (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name text NOT NULL,
  major text DEFAULT '',
  year integer DEFAULT 1 CHECK (year >= 1 AND year <= 4),
  high_school_gpa numeric DEFAULT 0.0 CHECK (high_school_gpa >= 0.0 AND high_school_gpa <= 4.0),
  age integer CHECK (age >= 16 AND age <= 100),
  gender text DEFAULT '',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create courses table
CREATE TABLE IF NOT EXISTS courses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code text UNIQUE NOT NULL,
  title text NOT NULL,
  description text DEFAULT '',
  credits integer DEFAULT 3 CHECK (credits > 0),
  difficulty text DEFAULT 'Intermediate' CHECK (difficulty IN ('Beginner', 'Intermediate', 'Advanced')),
  topics text[] DEFAULT '{}',
  department text DEFAULT '',
  created_at timestamptz DEFAULT now()
);

-- Create enrollments table
CREATE TABLE IF NOT EXISTS enrollments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  course_id uuid NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  semester text NOT NULL CHECK (semester IN ('Fall', 'Spring', 'Summer')),
  year integer NOT NULL CHECK (year >= 2020 AND year <= 2030),
  grade numeric CHECK (grade >= 0.0 AND grade <= 4.0),
  letter_grade text DEFAULT '',
  status text DEFAULT 'in_progress' CHECK (status IN ('completed', 'in_progress', 'dropped')),
  attendance_rate numeric DEFAULT 0.0 CHECK (attendance_rate >= 0.0 AND attendance_rate <= 100.0),
  assignment_completion_rate numeric DEFAULT 0.0 CHECK (assignment_completion_rate >= 0.0 AND assignment_completion_rate <= 100.0),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE(student_id, course_id, semester, year)
);

-- Create interactions table
CREATE TABLE IF NOT EXISTS interactions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  course_id uuid NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  event_type text NOT NULL CHECK (event_type IN ('video_watch', 'forum_post', 'assignment_submit', 'quiz_attempt', 'resource_view')),
  value numeric DEFAULT 0.0,
  timestamp timestamptz DEFAULT now()
);

-- Create recommendation_feedback table
CREATE TABLE IF NOT EXISTS recommendation_feedback (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  course_id uuid NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  recommended_at timestamptz DEFAULT now(),
  clicked boolean DEFAULT false,
  enrolled boolean DEFAULT false,
  outcome_grade numeric CHECK (outcome_grade IS NULL OR (outcome_grade >= 0.0 AND outcome_grade <= 4.0)),
  feedback_rating integer CHECK (feedback_rating IS NULL OR (feedback_rating >= 1 AND feedback_rating <= 5)),
  created_at timestamptz DEFAULT now()
);

-- Create model_metadata table
CREATE TABLE IF NOT EXISTS model_metadata (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  model_type text NOT NULL CHECK (model_type IN ('grade_predictor', 'recommender')),
  version text NOT NULL,
  metrics jsonb DEFAULT '{}',
  trained_at timestamptz DEFAULT now(),
  is_active boolean DEFAULT false
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_status ON enrollments(status);
CREATE INDEX IF NOT EXISTS idx_interactions_student_id ON interactions(student_id);
CREATE INDEX IF NOT EXISTS idx_interactions_course_id ON interactions(course_id);
CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_recommendation_feedback_student_id ON recommendation_feedback(student_id);
CREATE INDEX IF NOT EXISTS idx_model_metadata_active ON model_metadata(is_active) WHERE is_active = true;

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendation_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_metadata ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
  ON profiles FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = id);

-- Courses policies (everyone can view courses)
CREATE POLICY "Anyone can view courses"
  ON courses FOR SELECT
  TO authenticated
  USING (true);

-- Enrollments policies
CREATE POLICY "Users can view own enrollments"
  ON enrollments FOR SELECT
  TO authenticated
  USING (student_id = auth.uid());

CREATE POLICY "Users can create own enrollments"
  ON enrollments FOR INSERT
  TO authenticated
  WITH CHECK (student_id = auth.uid());

CREATE POLICY "Users can update own enrollments"
  ON enrollments FOR UPDATE
  TO authenticated
  USING (student_id = auth.uid())
  WITH CHECK (student_id = auth.uid());

-- Interactions policies
CREATE POLICY "Users can view own interactions"
  ON interactions FOR SELECT
  TO authenticated
  USING (student_id = auth.uid());

CREATE POLICY "Users can create own interactions"
  ON interactions FOR INSERT
  TO authenticated
  WITH CHECK (student_id = auth.uid());

-- Recommendation feedback policies
CREATE POLICY "Users can view own feedback"
  ON recommendation_feedback FOR SELECT
  TO authenticated
  USING (student_id = auth.uid());

CREATE POLICY "Users can create own feedback"
  ON recommendation_feedback FOR INSERT
  TO authenticated
  WITH CHECK (student_id = auth.uid());

CREATE POLICY "Users can update own feedback"
  ON recommendation_feedback FOR UPDATE
  TO authenticated
  USING (student_id = auth.uid())
  WITH CHECK (student_id = auth.uid());

-- Model metadata policies (read-only for all authenticated users)
CREATE POLICY "Authenticated users can view model metadata"
  ON model_metadata FOR SELECT
  TO authenticated
  USING (true);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_enrollments_updated_at
  BEFORE UPDATE ON enrollments
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();