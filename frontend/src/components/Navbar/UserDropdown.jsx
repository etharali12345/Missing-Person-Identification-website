import { NavLink } from "react-router";
import { activeClass } from "../../utils/navHelper.js";
import { LogoutButton } from "./LogoutButton.jsx";
import ProfileButton from "./ProfileButton";
import { HardDriveUpload, LogOut, UserRound } from "lucide-react";

export function UserDropdown() {
  const dropdownPaths = ["/profile", "/my-reports", "/logout"];
  const dropItemClass = activeClass("dropdown-item py-2");

  return (
    <div className="dropdown me-1">
      <ProfileButton dropdownPaths={dropdownPaths} />
      <ul className="dropdown-menu pb-0">
        <li>
          <NavLink to="/profile" className={dropItemClass}>
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
        <hr className="dropdown-divider m-0 " />
        <li>
          <LogoutButton />
        </li>
      </ul>
    </div>
  );
}
