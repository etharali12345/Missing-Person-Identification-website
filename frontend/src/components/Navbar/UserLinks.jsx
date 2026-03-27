import { NavLink, useLocation } from "react-router";
import { activeClass } from "../../utils/navHelper.js";

export function UserLinks() {
  const navClass = activeClass("nav-link");

  return (
    <li className="nav-item">
      <NavLink to="report-missing" className={navClass}>
        ابلاغ عن مفقود
      </NavLink>
    </li>
  );
}
