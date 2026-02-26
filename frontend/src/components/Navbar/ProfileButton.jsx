import { CircleUserRound, ChevronDown } from "lucide-react";
import { useLocation } from "react-router";

function ProfileButton({ dropdownPaths }) {
  const location = useLocation();
  const isDropdownActive = dropdownPaths.includes(location.pathname);

  return (
    <button
      type="button"
      className={`btn-profile ${isDropdownActive ? "active-pill" : ""}`}
      data-bs-toggle="dropdown"
      aria-expanded="false"
    >
      <ChevronDown size={16} strokeWidth={3} className="ms-1 downArrow-icon" />
      <CircleUserRound size={30} strokeWidth={1.7} className="profile-icon" />
    </button>
  );
}

export default ProfileButton;
