import { Lock } from "lucide-react";
import { LoginForm } from "./LoginForm";
import { NavLink } from "react-router";
import "./login.css";

export function LoginPage() {
  return (
    <div className="container-fluid p-5 d-flex justify-content-center min-vh-100   login-container">
      <div className="glass-card">
        <div className="text-center mb-4">
          <div className="icon-wrapper">
            <Lock size={48} strokeWidth={2} color="#27a86c" />
          </div>
          <h1 className="h4 fw-bold text-dark">تسجيل الدخول</h1>
          <p className="text-secondary small">
            مرحباً بك مجدداً، يرجى إدخال بياناتك
          </p>
        </div>
        <LoginForm />
        <p className="text-center text-secondary small mt-3">
          ليس لديك حساب؟
          <NavLink
            to="/signup"
            className="fw-bold text-decoration-none"
            style={{ color: "var(--primaryBlue)" }}
          >
            إنشاء حساب جديد
          </NavLink>
        </p>
      </div>
    </div>
  );
}
