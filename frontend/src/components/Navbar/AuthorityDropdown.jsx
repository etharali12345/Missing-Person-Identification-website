import { NavLink } from "react-router";
import ProfileButton from "./ProfileButton";
import { activeClass } from "../../utils/navHelper.js";
import { LogoutButton } from "./LogoutButton.jsx";
import { HardDriveUpload, UserRound, LogOut } from "lucide-react";

export function AuthorityDropdown() {
  const dropdownPaths = ["/authority-profile", "/my-found-reports", "/logout"];
  const dropItemClass = activeClass("dropdown-item py-2");

  return (
    <div className="dropdown me-1">
      <ProfileButton dropdownPaths={dropdownPaths} />
      <ul className="dropdown-menu pb-0">
        <li>
          <NavLink to="/authority-profile" className={dropItemClass}>
            <UserRound size={20} className="ms-2" />
            الملف التعريفي للجهة
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
          <LogoutButton />
        </li>
      </ul>
    </div>
  );
}
