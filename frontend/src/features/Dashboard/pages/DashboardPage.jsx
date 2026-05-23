import { useDashboard } from "../hooks/useDashboard";
import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { RegistrationPanel } from "../components/RegistrationPanel";

export function DashboardPage() {
  const location = useLocation();
  const { authorities, getAuthorities, getAuthorityById } = useDashboard();

  useEffect(() => {
    if (location.state?.refreshNeeded) {
      getAuthorities();
    }
  }, [location.key]);

  return (
    <div className="container dashboard-page pt-5 pb-5 mb-3">
      <RegistrationPanel
        authorities={authorities}
        getAuthorityById={getAuthorityById}
      />
    </div>
  );
}
