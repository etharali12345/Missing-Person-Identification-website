import { NavLink } from "react-router";
import { LogIn } from "lucide-react";
import { activeClass } from "../../utils/navHelper.js";

export function LoginButton() {
  const navClass = activeClass("btn-login");
  return (
    <NavLink to="/login" className={navClass}>
      تسجيل الدخول
      <LogIn size={20} strokeWidth={2} className="profile-icon me-1" />
    </NavLink>
  );
}
