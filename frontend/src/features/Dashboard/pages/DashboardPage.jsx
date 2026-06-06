import { useDashboard } from "../hooks/useDashboard";
import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { RegistrationPanel } from "../components/RegistrationPanel";
import { StatCards } from "../components/StatCards";

export function DashboardPage() {
  const location = useLocation();
  const { authorities, getAuthorities, getAuthorityById, stats } =
    useDashboard();

  useEffect(() => {
    if (location.state?.refreshNeeded) {
      getAuthorities();
    }
  }, [location.key]);

  return (
    <div className="container dashboard-page pt-5 pb-5 mb-3">
      <StatCards
        pendingCount={stats.pendingCount}
        missingCount={stats.missingCount}
        foundCount={stats.foundCount}
      />
      <RegistrationPanel
        authorities={authorities}
        getAuthorityById={getAuthorityById}
      />
    </div>
  );
}
