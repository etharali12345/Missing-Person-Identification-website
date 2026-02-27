import { Routes, Route } from "react-router";
import { MainLayout } from "./layouts/MainLayout.jsx";
import { LoginPage } from "./features/public/LoginPage.jsx";
import { SignUpPage } from "./features/public/SignUpPag.jsx";
import { Home } from "./pages/Home.jsx";
import { Unauthorized } from "./pages/Unauthorized.jsx";
import { RequiredAuth } from "./components/auth/RequiredAuth.jsx";
import { GuestOnly } from "./components/auth/GuestOnly.jsx";

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
          <Route path="/admin-dashboard" element={<Home />} />
          <Route path="/admin-profile" element={<Home />} />
          <Route path="/founded-database" element={<Home />} />
        </Route>

        <Route element={<RequiredAuth role={["admin", "authority"]} />}>
          <Route path="/missing-database" element={<Home />} />
          <Route path="/report-found" element={<Home />} />
          <Route path="/my-found-reports" element={<Home />} />
        </Route>

        <Route element={<RequiredAuth role={["admin", "user"]} />}>
          <Route path="/report-missing" element={<Home />} />
          <Route path="/my-reports" element={<Home />} />
        </Route>
      </Route>
    </Routes>
  );
}
