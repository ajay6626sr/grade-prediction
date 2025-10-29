import { useEffect, useState } from 'react';
import { apiService, Stats } from '../lib/api';
import { supabase } from '../lib/supabase';
import { BookOpen, TrendingUp, Award, Target } from 'lucide-react';

interface Profile {
  full_name: string;
  major: string;
  year: number;
  high_school_gpa: number;
}

export default function Dashboard({ userId }: { userId: string }) {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, [userId]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      const profileResponse = await supabase
        .table('profiles')
        .select('*')
        .eq('id', userId)
        .single();

      if (profileResponse.data) {
        setProfile(profileResponse.data);
      }

      const statsData = await apiService.getStats();
      setStats(statsData);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const yearLabels = ['Freshman', 'Sophomore', 'Junior', 'Senior'];

  return (
    <div className="space-y-8">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h2 className="text-2xl font-bold text-slate-900 mb-4">
          Welcome back, {profile?.full_name || 'Student'}!
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-slate-600">Major</p>
            <p className="text-lg font-semibold text-slate-900">
              {profile?.major || 'Not set'}
            </p>
          </div>
          <div>
            <p className="text-sm text-slate-600">Year</p>
            <p className="text-lg font-semibold text-slate-900">
              {profile ? yearLabels[profile.year - 1] : 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-sm text-slate-600">High School GPA</p>
            <p className="text-lg font-semibold text-slate-900">
              {profile?.high_school_gpa?.toFixed(2) || 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-sm text-slate-600">Current GPA</p>
            <p className="text-lg font-semibold text-blue-600">
              {stats?.current_gpa?.toFixed(2) || 'N/A'}
            </p>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={<BookOpen className="h-6 w-6 text-blue-600" />}
          title="Total Courses"
          value={stats?.total_courses || 0}
          bgColor="bg-blue-50"
        />

        <StatCard
          icon={<Award className="h-6 w-6 text-green-600" />}
          title="Completed"
          value={stats?.completed_courses || 0}
          bgColor="bg-green-50"
        />

        <StatCard
          icon={<Target className="h-6 w-6 text-orange-600" />}
          title="In Progress"
          value={stats?.in_progress_courses || 0}
          bgColor="bg-orange-50"
        />

        <StatCard
          icon={<TrendingUp className="h-6 w-6 text-purple-600" />}
          title="Total Credits"
          value={stats?.total_credits || 0}
          bgColor="bg-purple-50"
        />
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-xl font-bold text-slate-900 mb-4">Academic Progress</h3>

        {stats && stats.completed_courses > 0 ? (
          <div className="space-y-6">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium text-slate-700">
                  Average Grade
                </span>
                <span className="text-sm font-bold text-blue-600">
                  {stats.average_grade.toFixed(2)} / 4.0
                </span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-3">
                <div
                  className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${(stats.average_grade / 4.0) * 100}%` }}
                ></div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-200">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">
                  {stats.completed_courses}
                </p>
                <p className="text-sm text-slate-600 mt-1">Courses Completed</p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">
                  {stats.total_credits}
                </p>
                <p className="text-sm text-slate-600 mt-1">Credits Earned</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <BookOpen className="h-16 w-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-600 mb-2">No completed courses yet</p>
            <p className="text-sm text-slate-500">
              Start enrolling in courses to see your progress
            </p>
          </div>
        )}
      </div>

      <div className="bg-gradient-to-br from-blue-50 to-slate-50 rounded-xl border border-blue-100 p-6">
        <h3 className="text-lg font-bold text-slate-900 mb-3">Quick Actions</h3>
        <div className="space-y-3">
          <QuickActionButton
            icon={<TrendingUp className="h-5 w-5" />}
            title="Get Course Recommendations"
            description="Discover courses tailored to your interests"
          />
          <QuickActionButton
            icon={<Target className="h-5 w-5" />}
            title="Predict Grades"
            description="See your expected performance in courses"
          />
        </div>
      </div>
    </div>
  );
}

function StatCard({
  icon,
  title,
  value,
  bgColor,
}: {
  icon: React.ReactNode;
  title: string;
  value: number;
  bgColor: string;
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className={`${bgColor} rounded-lg w-12 h-12 flex items-center justify-center mb-4`}>
        {icon}
      </div>
      <p className="text-sm text-slate-600 mb-1">{title}</p>
      <p className="text-3xl font-bold text-slate-900">{value}</p>
    </div>
  );
}

function QuickActionButton({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <button className="w-full flex items-center space-x-4 p-4 bg-white rounded-lg border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all text-left">
      <div className="flex-shrink-0 text-blue-600">{icon}</div>
      <div>
        <p className="font-semibold text-slate-900">{title}</p>
        <p className="text-sm text-slate-600">{description}</p>
      </div>
    </button>
  );
}
