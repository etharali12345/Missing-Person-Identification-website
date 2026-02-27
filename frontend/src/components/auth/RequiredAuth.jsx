import { Outlet } from "react-router";
import { useAuth } from "../../context/AuthContext";
import { Navigate } from "react-router";

export function RequiredAuth({ role }) {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) return null;

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  if (role && !role.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
}
