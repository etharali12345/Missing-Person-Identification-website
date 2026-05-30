import { LogOut } from "lucide-react";
import { useAuth } from "../../context/AuthContext.jsx";
import { useNavigate } from "react-router-dom";

export function LogoutButton() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login", { replace: true });
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <button onClick={handleLogout} className="dropdown-item py-2">
      <LogOut size={20} className="ms-2 " />
      تسجيل الخروج
    </button>
  );
}
