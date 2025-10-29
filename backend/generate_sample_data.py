"""
Generate sample enrollment and interaction data for model training
"""
import random
import os
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)


def generate_sample_enrollments(num_students=50, num_enrollments_per_student=8):
    """Generate sample enrollment data"""

    courses_response = supabase.table('courses').select('id, difficulty').execute()
    courses = courses_response.data

    if not courses:
        print("No courses found. Please add courses first.")
        return

    print(f"Generating sample data for {num_students} students...")

    difficulty_base_grades = {
        'Beginner': 3.2,
        'Intermediate': 2.8,
        'Advanced': 2.5
    }

    for student_num in range(1, num_students + 1):
        email = f"student{student_num}@example.com"
        password = "password123"

        try:
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            if not auth_response.user:
                print(f"✗ Failed to create user {email}")
                continue

            student_id = auth_response.user.id

            profile_data = {
                "id": student_id,
                "full_name": f"Student {student_num}",
                "major": random.choice(["Computer Science", "Mathematics", "Physics", "Business", "Economics"]),
                "year": random.randint(1, 4),
                "high_school_gpa": round(random.uniform(2.5, 4.0), 2),
                "age": random.randint(18, 25),
                "gender": random.choice(["M", "F", "Other"])
            }

            supabase.table('profiles').insert(profile_data).execute()

            student_ability = random.uniform(-0.5, 0.5)

            selected_courses = random.sample(courses, min(num_enrollments_per_student, len(courses)))

            for i, course in enumerate(selected_courses):
                difficulty = course['difficulty']
                base_grade = difficulty_base_grades.get(difficulty, 2.8)

                grade = base_grade + student_ability + random.uniform(-0.3, 0.3)
                grade = max(0.0, min(4.0, grade))

                attendance_rate = random.uniform(70, 100)
                assignment_completion = random.uniform(60, 100)

                if grade > 3.0:
                    attendance_rate = random.uniform(85, 100)
                    assignment_completion = random.uniform(85, 100)
                elif grade < 2.0:
                    attendance_rate = random.uniform(50, 75)
                    assignment_completion = random.uniform(50, 75)

                status = 'completed' if i < num_enrollments_per_student - 2 else random.choice(['completed', 'in_progress'])

                enrollment_data = {
                    "student_id": student_id,
                    "course_id": course['id'],
                    "semester": random.choice(['Fall', 'Spring']),
                    "year": random.choice([2023, 2024]),
                    "grade": round(grade, 2) if status == 'completed' else None,
                    "status": status,
                    "attendance_rate": round(attendance_rate, 1),
                    "assignment_completion_rate": round(assignment_completion, 1)
                }

                try:
                    supabase.table('enrollments').insert(enrollment_data).execute()
                except Exception as e:
                    pass

            num_interactions = random.randint(10, 50)
            for _ in range(num_interactions):
                interaction_data = {
                    "student_id": student_id,
                    "course_id": random.choice(selected_courses)['id'],
                    "event_type": random.choice(['video_watch', 'forum_post', 'assignment_submit', 'quiz_attempt']),
                    "value": random.uniform(1, 120)
                }

                try:
                    supabase.table('interactions').insert(interaction_data).execute()
                except Exception as e:
                    pass

            print(f"✓ Created student {student_num}/{num_students}")

        except Exception as e:
            print(f"✗ Error creating student {email}: {e}")

    print(f"\n✓ Sample data generation complete!")
    print(f"  - {num_students} students created")
    print(f"  - ~{num_students * num_enrollments_per_student} enrollments created")
    print(f"  - Interaction data generated")


if __name__ == '__main__':
    print("=" * 60)
    print("Sample Data Generator")
    print("=" * 60)
    print("\nThis will create sample students, enrollments, and interactions.")
    print("Note: Some duplicates may be skipped if data already exists.\n")

    generate_sample_enrollments(num_students=50, num_enrollments_per_student=8)
