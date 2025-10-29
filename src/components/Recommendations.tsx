import { useState } from 'react';
import { apiService, CourseRecommendation } from '../lib/api';
import { Sparkles, TrendingUp, BookOpen, Award } from 'lucide-react';

export default function Recommendations({ userId }: { userId: string }) {
  const [recommendations, setRecommendations] = useState<CourseRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getRecommendations(userId, 10);
      setRecommendations(response.recommendations);
    } catch (err: any) {
      setError(err.message || 'Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Beginner':
        return 'bg-green-100 text-green-800';
      case 'Intermediate':
        return 'bg-yellow-100 text-yellow-800';
      case 'Advanced':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-slate-100 text-slate-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl shadow-lg p-8 text-white">
        <div className="flex items-center space-x-3 mb-4">
          <Sparkles className="h-8 w-8" />
          <h2 className="text-3xl font-bold">AI-Powered Recommendations</h2>
        </div>
        <p className="text-blue-100 mb-6">
          Get personalized course recommendations based on your academic history and interests
        </p>
        <button
          onClick={loadRecommendations}
          disabled={loading}
          className="bg-white text-blue-600 hover:bg-blue-50 font-semibold px-6 py-3 rounded-lg transition-colors disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Get Recommendations'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {recommendations.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-slate-900">
            Recommended Courses for You
          </h3>

          <div className="grid gap-4">
            {recommendations.map((rec, index) => (
              <div
                key={rec.course_id}
                className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-600 rounded-full font-bold text-sm">
                        {index + 1}
                      </span>
                      <h4 className="text-lg font-bold text-slate-900">
                        {rec.course_title}
                      </h4>
                    </div>
                    <p className="text-sm text-slate-600 mb-3">{rec.course_code}</p>

                    <div className="flex flex-wrap gap-2">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${getDifficultyColor(
                          rec.difficulty
                        )}`}
                      >
                        {rec.difficulty}
                      </span>
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700">
                        {rec.department}
                      </span>
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                        {rec.credits} Credits
                      </span>
                    </div>
                  </div>

                  <div className="ml-4 text-right">
                    <div className="flex items-center space-x-2 mb-2">
                      <TrendingUp className="h-5 w-5 text-blue-600" />
                      <span className="text-2xl font-bold text-blue-600">
                        {(rec.score * 100).toFixed(0)}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600">Match Score</p>
                  </div>
                </div>

                {rec.predicted_grade !== null && (
                  <div className="bg-gradient-to-r from-blue-50 to-slate-50 rounded-lg p-4 border border-blue-100">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Award className="h-5 w-5 text-blue-600" />
                        <span className="text-sm font-medium text-slate-700">
                          Predicted Grade
                        </span>
                      </div>
                      <span className="text-xl font-bold text-blue-600">
                        {rec.predicted_grade.toFixed(2)}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && recommendations.length === 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center">
          <BookOpen className="h-16 w-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 mb-2">
            No Recommendations Yet
          </h3>
          <p className="text-slate-600 mb-6">
            Click the button above to generate personalized course recommendations
          </p>
        </div>
      )}
    </div>
  );
}
