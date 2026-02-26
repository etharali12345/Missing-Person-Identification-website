import { useState } from "react";
import { useNavigate } from "react-router";
import { useAuth } from "../../context/AuthContext.jsx";

export function LoginForm() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email_or_phone, setEmailOrPhone] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [validated, setValidated] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleEmailOrPhoneChange = (e) => {
    setEmailOrPhone(e.target.value);
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
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
      await login(email_or_phone, password);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form
        noValidate
        className={`needs-validation ${validated ? "was-validated" : ""}`}
        onSubmit={handleSubmit}
      >
        <div className="mb-3">
          <label className="form-label">البريد الإلكتروني / رقم الهاتف</label>
          <input
            type="text"
            className="form-control"
            required
            value={email_or_phone}
            onChange={handleEmailOrPhoneChange}
          />
          <div className="invalid-feedback">
            الرجاء إدخال البريد الإلكتروني أو رقم الهاتف
          </div>
        </div>

        <div className="mb-4">
          <label className="form-label">كلمة المرور</label>
          <input
            type="password"
            className="form-control"
            required
            minLength={6}
            value={password}
            onChange={handlePasswordChange}
          />
          <div className="invalid-feedback">الرجاء إدخال كلمة المرور</div>
        </div>
        {error && (
          <div
            className="alert alert-danger d-flex align-items-center"
            role="alert"
          >
            {error}
          </div>
        )}
        <button type="submit" className="btn btn-success btn-custom w-100 mb-4">
          دخول
        </button>
      </form>
    </div>
  );
}
