import { useDashboard } from "../hooks/useDashboard";
import { RegistrationPanel } from "../components/RegistrationPanel";

export function DashboardPage() {
  const { authorities } = useDashboard();

  return (
    <div className="container dashboard-page pt-5">
      <h1>لوحة الإدارة</h1>
      <RegistrationPanel authorities={authorities} />
    </div>
  );
}
