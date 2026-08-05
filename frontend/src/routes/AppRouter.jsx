import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from '../components/layout/AppLayout';
import { useAuth } from '../context/AuthContext';
import { ProtectedRoute, RoleRoute } from './ProtectedRoute';
import { ROLES, homePathForRole } from '../utils/helpers';

import LoginPage from '../pages/LoginPage';
import ForgotPasswordPage from '../pages/ForgotPasswordPage';
import UnauthorizedPage from '../pages/UnauthorizedPage';
import NotFoundPage from '../pages/NotFoundPage';
import PersonalDashboard from '../pages/PersonalDashboard';
import TaskListPage from '../pages/TaskListPage';
import TaskFormPage from '../pages/TaskFormPage';
import TaskDetailPage from '../pages/TaskDetailPage';
import ReviewTaskPage from '../pages/ReviewTaskPage';
import SupervisorDashboard from '../pages/SupervisorDashboard';
import PendingReviewsPage from '../pages/PendingReviewsPage';
import TeamPage from '../pages/TeamPage';
import AdminDashboard from '../pages/AdminDashboard';
import UserManagementPage from '../pages/UserManagementPage';
import DepartmentManagementPage from '../pages/DepartmentManagementPage';
import CategoryManagementPage from '../pages/CategoryManagementPage';
import KpiWeightsPage from '../pages/KpiWeightsPage';
import AttendancePage from '../pages/AttendancePage';
import ProfilePage from '../pages/ProfilePage';
import ReportsPage from '../pages/ReportsPage';

function HomeRedirect() {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={homePathForRole(user.role)} replace />;
}

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/unauthorized" element={<UnauthorizedPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<HomeRedirect />} />

          <Route
            path="/dashboard"
            element={
              <RoleRoute roles={[ROLES.INTERN, ROLES.STAFF, ROLES.SUPERVISOR, ROLES.ADMIN]}>
                <PersonalDashboard />
              </RoleRoute>
            }
          />

          <Route path="/tasks" element={<TaskListPage />} />
          <Route path="/tasks/new" element={<TaskFormPage />} />
          <Route path="/tasks/:id" element={<TaskDetailPage />} />
          <Route path="/tasks/:id/edit" element={<TaskFormPage />} />
          <Route
            path="/tasks/:id/review"
            element={
              <RoleRoute roles={[ROLES.SUPERVISOR, ROLES.ADMIN]}>
                <ReviewTaskPage />
              </RoleRoute>
            }
          />

          <Route path="/attendance" element={<AttendancePage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/profile" element={<ProfilePage />} />

          <Route
            path="/supervisor"
            element={
              <RoleRoute roles={[ROLES.SUPERVISOR, ROLES.ADMIN]}>
                <SupervisorDashboard />
              </RoleRoute>
            }
          />
          <Route
            path="/supervisor/pending"
            element={
              <RoleRoute roles={[ROLES.SUPERVISOR, ROLES.ADMIN]}>
                <PendingReviewsPage />
              </RoleRoute>
            }
          />
          <Route
            path="/supervisor/team"
            element={
              <RoleRoute roles={[ROLES.SUPERVISOR, ROLES.ADMIN]}>
                <TeamPage mode="members" />
              </RoleRoute>
            }
          />
          <Route
            path="/supervisor/performance"
            element={
              <RoleRoute roles={[ROLES.SUPERVISOR, ROLES.ADMIN]}>
                <TeamPage mode="performance" />
              </RoleRoute>
            }
          />

          <Route
            path="/admin"
            element={
              <RoleRoute roles={[ROLES.ADMIN]}>
                <AdminDashboard />
              </RoleRoute>
            }
          />
          <Route
            path="/admin/users"
            element={
              <RoleRoute roles={[ROLES.ADMIN]}>
                <UserManagementPage />
              </RoleRoute>
            }
          />
          <Route
            path="/admin/departments"
            element={
              <RoleRoute roles={[ROLES.ADMIN]}>
                <DepartmentManagementPage />
              </RoleRoute>
            }
          />
          <Route
            path="/admin/categories"
            element={
              <RoleRoute roles={[ROLES.ADMIN]}>
                <CategoryManagementPage />
              </RoleRoute>
            }
          />
          <Route
            path="/admin/kpi-weights"
            element={
              <RoleRoute roles={[ROLES.ADMIN]}>
                <KpiWeightsPage />
              </RoleRoute>
            }
          />
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
