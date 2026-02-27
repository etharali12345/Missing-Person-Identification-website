import { NavLink } from "react-router";
import { activeClass } from "../../utils/navHelper.js";

export function MainLinks() {
  const navClass = activeClass("nav-link");

  return (
    <>
      <li className="nav-item">
        <NavLink to="/" className={navClass}>
          الرئيسية
        </NavLink>
      </li>
      <li className="nav-item">
        <NavLink to="/how-we-help" className={navClass}>
          كيف نساعدك
        </NavLink>
      </li>
      <li className="nav-item">
        <NavLink to="/about" className={navClass}>
          من نحن
        </NavLink>
      </li>
    </>
  );
}
