import { NavLink } from "react-router";
import { activeClass } from "../../utils/navHelper.js";
import { HardDriveUpload, UserRound, LogOut } from "lucide-react";
import ProfileButton from "./ProfileButton";

export function AdminDropdown() {
  const dropdownPaths = [
    "/admin-profile",
    "/logout",
    "/my-reports",
    "/my-found-reports",
  ];
  const dropItemClass = activeClass("dropdown-item py-2");

  return (
    <div className="dropdown me-1">
      <ProfileButton dropdownPaths={dropdownPaths} />
      <ul className="dropdown-menu pb-0">
        <li>
          <NavLink to="/admin-profile" className={dropItemClass}>
            <UserRound size={20} className="ms-2" />
            الملف الشخصي
          </NavLink>
        </li>
        <hr className="dropdown-divider m-0" />
        <li>
          <NavLink to="/my-reports" className={dropItemClass}>
            <HardDriveUpload size={20} className="ms-2" />
            بلاغات مفقودين رفعتها
          </NavLink>
        </li>
        <hr className="dropdown-divider m-0" />
        <li>
          <NavLink to="/my-found-reports" className={dropItemClass}>
            <HardDriveUpload size={20} className="ms-2" />
            بلاغات عثور رفعتها
          </NavLink>
        </li>
        <hr className="dropdown-divider m-0 " />
        <li>
          <NavLink to="/logout" className={dropItemClass}>
            <LogOut size={20} className="ms-2" />
            تسجيل الخروج
          </NavLink>
        </li>
      </ul>
    </div>
  );
}
