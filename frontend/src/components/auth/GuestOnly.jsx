import { Outlet } from "react-router";
import { useAuth } from "../../context/AuthContext";
import { Navigate } from "react-router";

export const GuestOnly = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) return null;

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
};
