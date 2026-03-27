import { NavLink, useLocation } from "react-router";
import { activeClass } from "../../utils/navHelper.js";
import { ChevronDown, ClipboardPlus, Database } from "lucide-react";

export function AdminLinks() {
  const location = useLocation();
  const dropdownPaths = [
    "/founded-database",
    "/missing-database",
    "/report-missing",
    "/report-found",
  ];
  const isDropdownActive = dropdownPaths.includes(location.pathname);
  const navClass = activeClass("nav-link");
  const dropItemClass = activeClass("dropdown-item py-2");

  return (
    <>
      <li className="nav-item">
        <NavLink to="/admin-dashboard" className={navClass}>
          لوحة التحكم
        </NavLink>
      </li>
      <li className="nav-item dropdown">
        <button
          className={`nav-link ${isDropdownActive ? "active-pill" : ""} `}
          data-bs-toggle="dropdown"
          aria-expanded="false"
        >
          الخدمات
          <ChevronDown
            size={16}
            strokeWidth={3}
            className="me-1 downArrow-icon"
          />
        </button>
        <ul className="dropdown-menu mt-2 pb-0">
          <li>
            <NavLink to="/report-missing" className={dropItemClass}>
              <ClipboardPlus size={20} className="ms-2 icon" />
              ابلاغ عن مققود
            </NavLink>
          </li>
          <hr className="dropdown-divider m-0" />
          <li>
            <NavLink to="/report-found" className={dropItemClass}>
              <ClipboardPlus size={20} className="ms-2 icon" />
              ابلاغ عن العثور
            </NavLink>
          </li>
          <hr className="dropdown-divider m-0" />
          <li>
            <NavLink to="/missing-database" className={dropItemClass}>
              <Database size={20} className="ms-2 icon" />
              قاعدة بيانات المفقودين
            </NavLink>
          </li>
          <hr className="dropdown-divider m-0" />
          <li>
            <NavLink to="/founded-database" className={dropItemClass}>
              <Database size={20} className="ms-2 icon" />
              قاعدة بيانات المعثورين
            </NavLink>
          </li>
        </ul>
      </li>
    </>
  );
}
