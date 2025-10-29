import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { apiService, PredictGradeResponse } from '../lib/api';
import { BookOpen, TrendingUp, Award, Search } from 'lucide-react';

interface Course {
  id: string;
  code: string;
  title: string;
  description: string;
  credits: number;
  difficulty: string;
  department: string;
  topics: string[];
}

export default function CourseList({ userId }: { userId: string }) {
  const [courses, setCourses] = useState<Course[]>([]);
  const [filteredCourses, setFilteredCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('All');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  const [predicting, setPredicting] = useState<string | null>(null);
  const [predictions, setPredictions] = useState<Record<string, PredictGradeResponse>>({});

  useEffect(() => {
    loadCourses();
  }, []);

  useEffect(() => {
    filterCourses();
  }, [courses, searchTerm, selectedDepartment, selectedDifficulty]);

  const loadCourses = async () => {
    try {
      const response = await supabase.table('courses').select('*').order('code');
      if (response.data) {
        setCourses(response.data);
      }
    } catch (error) {
      console.error('Error loading courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterCourses = () => {
    let filtered = [...courses];

    if (searchTerm) {
      filtered = filtered.filter(
        (course) =>
          course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          course.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
          course.department.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedDepartment !== 'All') {
      filtered = filtered.filter((course) => course.department === selectedDepartment);
    }

    if (selectedDifficulty !== 'All') {
      filtered = filtered.filter((course) => course.difficulty === selectedDifficulty);
    }

    setFilteredCourses(filtered);
  };

  const handlePredictGrade = async (courseId: string) => {
    try {
      setPredicting(courseId);
      const prediction = await apiService.predictGrade(userId, courseId);
      setPredictions({ ...predictions, [courseId]: prediction });
    } catch (error: any) {
      alert(error.message || 'Failed to predict grade');
    } finally {
      setPredicting(null);
    }
  };

  const departments = ['All', ...new Set(courses.map((c) => c.department))];
  const difficulties = ['All', 'Beginner', 'Intermediate', 'Advanced'];

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Beginner':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'Intermediate':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Advanced':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <BookOpen className="h-8 w-8 text-blue-600" />
          <h2 className="text-2xl font-bold text-slate-900">Course Catalog</h2>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          <div className="relative md:col-span-3">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
            <input
              type="text"
              placeholder="Search courses..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <select
            value={selectedDepartment}
            onChange={(e) => setSelectedDepartment(e.target.value)}
            className="px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {departments.map((dept) => (
              <option key={dept} value={dept}>
                {dept === 'All' ? 'All Departments' : dept}
              </option>
            ))}
          </select>

          <select
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
            className="px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {difficulties.map((diff) => (
              <option key={diff} value={diff}>
                {diff === 'All' ? 'All Difficulties' : diff}
              </option>
            ))}
          </select>

          <div className="flex items-center text-sm text-slate-600">
            <span className="font-medium">{filteredCourses.length}</span>
            <span className="ml-1">courses found</span>
          </div>
        </div>
      </div>

      <div className="grid gap-4">
        {filteredCourses.map((course) => {
          const prediction = predictions[course.id];

          return (
            <div
              key={course.id}
              className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-xl font-bold text-slate-900">{course.title}</h3>
                  </div>
                  <p className="text-sm text-slate-600 mb-1">{course.code}</p>
                  <p className="text-slate-700 mb-4">{course.description}</p>

                  <div className="flex flex-wrap gap-2 mb-4">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium border ${getDifficultyColor(
                        course.difficulty
                      )}`}
                    >
                      {course.difficulty}
                    </span>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
                      {course.department}
                    </span>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700 border border-blue-200">
                      {course.credits} Credits
                    </span>
                  </div>

                  {course.topics && course.topics.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {course.topics.slice(0, 5).map((topic, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 text-xs bg-slate-50 text-slate-600 rounded border border-slate-200"
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="ml-6">
                  <button
                    onClick={() => handlePredictGrade(course.id)}
                    disabled={predicting === course.id}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 whitespace-nowrap"
                  >
                    <TrendingUp className="h-4 w-4" />
                    <span>
                      {predicting === course.id ? 'Predicting...' : 'Predict Grade'}
                    </span>
                  </button>
                </div>
              </div>

              {prediction && (
                <div className="mt-4 bg-gradient-to-r from-blue-50 to-slate-50 rounded-lg p-4 border border-blue-100">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Award className="h-5 w-5 text-blue-600" />
                      <span className="text-sm font-medium text-slate-700">
                        Predicted Grade
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl font-bold text-blue-600">
                          {prediction.predicted_grade.toFixed(2)}
                        </span>
                        <span className="px-3 py-1 bg-blue-600 text-white rounded-lg font-bold">
                          {prediction.letter_grade}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 mt-1">
                        Range: {prediction.grade_range.lower.toFixed(2)} -{' '}
                        {prediction.grade_range.upper.toFixed(2)}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {filteredCourses.length === 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center">
          <BookOpen className="h-16 w-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 mb-2">No Courses Found</h3>
          <p className="text-slate-600">
            Try adjusting your search or filter criteria
          </p>
        </div>
      )}
    </div>
  );
}
