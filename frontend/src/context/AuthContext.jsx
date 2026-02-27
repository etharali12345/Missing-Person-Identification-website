import {
  useState,
  createContext,
  useContext,
  useCallback,
  useEffect,
} from "react";
import {
  getMeService,
  loginService,
  singupService,
  logoutService,
} from "../services/AuthService";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      setLoading(true);
      const currentUser = await getMeService();
      setUser(currentUser);
      setLoading(false);
    };
    checkAuth();
  }, []);

  const login = useCallback(async (email_or_phone, password) => {
    const loggedUser = await loginService(email_or_phone, password);
    setUser(loggedUser);
  });

  const signup = useCallback(async (data) => {
    const loggedUser = await singupService(data);
    setUser(loggedUser);
  });

  const logout = useCallback(async () => {
    await logoutService();
    setUser(null);
  });

  const isAuthenticated = !!user;

  return (
    <AuthContext.Provider
      value={{ user, loading, login, signup, logout, isAuthenticated }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
