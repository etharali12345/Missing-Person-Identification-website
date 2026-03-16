import { NavLink } from "react-router";
import { LogIn } from "lucide-react";
import { useActiveClass } from "../../utils/navHelper.js";

export function LoginButton() {
  const navClass = useActiveClass("btn-login", ["/login", "/signup"]);
  return (
    <NavLink to="/login" className={navClass}>
      تسجيل الدخول
      <LogIn size={20} strokeWidth={2} className="profile-icon me-1" />
    </NavLink>
  );
}
