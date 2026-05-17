import { useState } from "react";
import { useNavigate } from "react-router";
import { useAuth } from "../../../context/AuthContext";
import { NormalSignUpForm } from "./NormalSignUpForm";
import { AuthoritySignUpForm } from "./AuthoritySignUpForm";
import { CircleCheckBig } from "lucide-react";

export function SignUpForm() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [role, setRole] = useState("user");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [validated, setValidated] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [userData, setUserData] = useState({
    email_or_phone: "",
    password: "",
    first_name: "",
    last_name: "",
    authority_type: "service",
    authority_name: "",
    location: "",
    license_number: "",
    document: null,
  });

  const handleDataChange = (data) => {
    setUserData((prev) => ({ ...prev, ...data }));
  };

  const handleRoleChange = (e) => {
    setRole(e.target.value);
    setValidated(false);
  };

  const handleEmailOrPhoneChange = (e) => {
    handleDataChange({ email_or_phone: e.target.value });
  };

  const handlePasswordChange = (e) => {
    handleDataChange({ password: e.target.value });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    if (!form.checkValidity()) {
      event.stopPropagation();
      setValidated(true);
      return;
    }
    setValidated(true);
    setError(null);
    setLoading(true);
    try {
      if (role === "user") {
        let payload = {
          role,
          first_name: userData.first_name,
          last_name: userData.last_name,
          email_or_phone: userData.email_or_phone,
          password: userData.password,
        };
        await signup(payload);
        navigate("/");
      }
      if (role === "authority") {
        const form = new FormData();
        form.append("role", role);
        form.append("authority_name", userData.authority_name);
        form.append("authority_type", userData.authority_type);
        form.append("location", userData.location);
        form.append("document", userData.document);
        form.append("email_or_phone", userData.email_or_phone);
        form.append("password", userData.password);
        if (userData.authority_type === "organization") {
          form.append("license_number", userData.license_number);
        }
        await signup(form);
        setSubmitted(true);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {submitted && role === "authority" ? (
        <div className="text-center py-4 pt-0">
          <div className="mb-4">
            <CircleCheckBig size={60} color="#198653" />
          </div>
          <h5 className="fw-bold mb-2">تم إرسال طلبك بنجاح</h5>
          <p className="text-muted">
            طلب تسجيل جهتك قيد المراجعة. سيتم إشعارك بعد موافقة المشرف.
          </p>
        </div>
      ) : (
        <div>
          <div className="nav-tabs-custom">
            <button
              value="user"
              onClick={handleRoleChange}
              className={`tab-btn ${role === "user" ? "tab-active" : ""}`}
            >
              مستخدم عادي
            </button>
            <button
              value="authority"
              onClick={handleRoleChange}
              className={`tab-btn ${role === "authority" ? "tab-active" : ""}`}
            >
              جهة رسمية
            </button>
          </div>

          <form
            noValidate
            onSubmit={handleSubmit}
            className={`needs-validation ${validated ? "was-validated" : ""}`}
          >
            {role === "user" ? (
              <NormalSignUpForm
                role={role}
                userData={userData}
                handleDataChange={handleDataChange}
              />
            ) : (
              <AuthoritySignUpForm
                role={role}
                userData={userData}
                handleDataChange={handleDataChange}
              />
            )}

            <div className="mb-3">
              <label className="form-label">البريد الإلكتروني أو الهاتف</label>
              <input
                type="text"
                required
                pattern="(\+?[0-9]{7,15}|[^\s@]+@[^\s@]+\.[^\s@]+)"
                className="form-control w-100"
                value={userData.email_or_phone}
                onChange={handleEmailOrPhoneChange}
              />
              <div className="invalid-feedback">
                يرجى إدخال بريد إلكتروني صحيح أو رقم هاتف صحيح
              </div>
            </div>

            <div className="mb-4">
              <label className="form-label">كلمة المرور</label>
              <input
                type="password"
                required
                minLength={6}
                className="form-control w-100"
                value={userData.password}
                onChange={handlePasswordChange}
              />
              <div className="invalid-feedback">
                يجب أن تكون كلمة المرور 6 أحرف على الأقل
              </div>
            </div>

            {error && (
              <div
                className="alert alert-danger d-flex justify-content-center align-items-center mb-3"
                role="alert"
              >
                {error}
              </div>
            )}
            <button type="submit" className="btn-custom w-100">
              تأكيد التسجيل
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
