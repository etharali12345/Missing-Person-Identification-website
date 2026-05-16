import { useDashboard } from "../hooks/useDashboard";
import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { RegistrationPanel } from "../components/RegistrationPanel";

export function DashboardPage() {
  const location = useLocation();
  const { authorities, getAuthorities } = useDashboard();

  useEffect(() => {
    if (location.state?.refreshNeeded) {
      getAuthorities();
    }
  }, [location.key]);

  return (
    <div className="container dashboard-page pt-5">
      <RegistrationPanel authorities={authorities} />
    </div>
  );
}
