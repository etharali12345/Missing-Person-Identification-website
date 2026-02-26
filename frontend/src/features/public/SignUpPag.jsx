import { SignUpForm } from "./SignUpForm";
import { UserRoundKey } from "lucide-react";
import { NavLink } from "react-router";
import "./login.css";
import "./signup.css";

export function SignUpPage() {
  return (
    <div className="container-fluid p-5 d-flex justify-content-center min-vh-100   login-container">
      <div className="glass-card">
        <div className="text-center mb-4">
          <div className="icon-wrapper">
            <UserRoundKey size={48} strokeWidth={2} color="#27a86c" />
          </div>
          <h1 className="h4 fw-bold text-dark">إنشاء حساب</h1>
          <p className="text-secondary small">
            اختر نوع الحساب وأكمل البيانات{" "}
          </p>
        </div>
        <SignUpForm />
        <p className="text-center text-secondary small mt-3">
          لديك حساب بالفعل؟{" "}
          <NavLink
            to="/login"
            className="fw-bold text-decoration-none"
            style={{ color: "var(--primaryBlue)" }}
          >
            تسجيل الدخول
          </NavLink>
        </p>
      </div>
    </div>
  );
}
