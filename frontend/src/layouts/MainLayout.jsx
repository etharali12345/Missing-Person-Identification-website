import { Outlet } from "react-router";
import { NavBar } from "../components/Navbar/Navbar.jsx";
import { Footer } from "../components/Footer/Footer.jsx";

export function MainLayout() {
  return (
    <div>
      <NavBar />
      <main className="min-vh-100">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
