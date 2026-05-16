import { Routes, Route } from "react-router";
import { MainLayout } from "./layouts/MainLayout.jsx";
import { LoginPage } from "./features/authorize/pages/LoginPage.jsx";
import { SignUpPage } from "./features/authorize/pages/SignUpPag";
import { MissingReportPage } from "./features/missingReport/pages/MissingReportPage.jsx";
import { FoundReportPage } from "./features/foundReport/pages/FoundReportPage.jsx";
import { Home } from "./pages/Home.jsx";
import { MyMissingReportsPage } from "./features/myMissingReports/pages/MyMissingReports.jsx";
import { MyFoundReportsPage } from "./features/myFoundReports/pages/MyFoundReports.jsx";
import { DashboardPage } from "./features/Dashboard/pages/DashboardPage.jsx";
import { Unauthorized } from "./pages/Unauthorized.jsx";
import { RequiredAuth } from "./components/auth/RequiredAuth.jsx";
import { GuestOnly } from "./components/auth/GuestOnly.jsx";
import { AuthorityDetailsPage } from "./features/Dashboard/pages/authorityDetialsPage.jsx";

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route index element={<Home />} />
        <Route path="/about" element={<Home />} />
        <Route path="/how-we-help" element={<Home />} />
        <Route path="/unauthorized" element={<Unauthorized />} />

        <Route path="/logout" element={<Home />} />

        <Route element={<GuestOnly />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignUpPage />} />
        </Route>

        <Route element={<RequiredAuth role={["user"]} />}>
          <Route path="/profile" element={<Home />} />
        </Route>

        <Route element={<RequiredAuth role={["authority"]} />}>
          <Route path="/authority-profile" element={<Home />} />
        </Route>

        <Route element={<RequiredAuth role={["admin"]} />}>
          <Route path="/admin-dashboard" element={<DashboardPage />} />
          <Route path="/authorityDetails" element={<AuthorityDetailsPage />} />
          <Route path="/founded-database" element={<Home />} />
        </Route>

        <Route element={<RequiredAuth role={["admin", "authority"]} />}>
          <Route path="/missing-database" element={<Home />} />
          <Route path="/report-found" element={<FoundReportPage />} />
          <Route path="/my-found-reports" element={<MyFoundReportsPage />} />
        </Route>

        <Route element={<RequiredAuth role={["admin", "user"]} />}>
          <Route path="/report-missing" element={<MissingReportPage />} />
          <Route path="/my-reports" element={<MyMissingReportsPage />} />
        </Route>
      </Route>
    </Routes>
  );
}
