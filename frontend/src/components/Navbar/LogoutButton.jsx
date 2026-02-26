import { LogOut } from "lucide-react";
import { useAuth } from "../../context/AuthContext.jsx";

export function LogoutButton() {
  const { logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
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
