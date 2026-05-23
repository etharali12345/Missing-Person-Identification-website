import { useEffect, useCallback } from "react";
import { UserRoundPen, BadgeCheck, Eye, EyeOff } from "lucide-react";
import { useState } from "react";
import { useProfile } from "../hooks/useProfile";
import "./profilePage.css";

export function ProfilePage() {
  const {
    profile,
    loading,
    updating,
    error,
    successMessage,
    handleProfile,
    resetState,
  } = useProfile();

  const [showOldPassword, setShowOldPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email_or_phone: "",
    old_password: "",
    new_password: "",
  });

  useEffect(() => {
    if (profile) {
      setFormData((prev) => ({
        ...prev,
        first_name: profile.first_name || "",
        last_name: profile.last_name || "",
        email_or_phone: profile.email_or_phone || "",
      }));
    }
  }, [profile]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setFieldErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const validate = () => {
    const errors = {};
    if (!formData.first_name.trim())
      errors.first_name = "يرجى إدخال الاسم الأول";
    if (!formData.last_name.trim())
      errors.last_name = "يرجى إدخال الاسم الأخير";
    if (!formData.email_or_phone.trim())
      errors.email_or_phone = "يرجى إدخال البريد الإلكتروني أو رقم الهاتف";
    if (!formData.old_password)
      errors.old_password = "يرجى إدخال كلمة المرور القديمة";
    if (!formData.new_password)
      errors.new_password = "يرجى إدخال كلمة المرور الجديدة";
    else if (formData.new_password.length < 6)
      errors.new_password = "كلمة المرور يجب أن تكون 6 أحرف على الأقل";
    return errors;
  };

  const handleSubmit = useCallback(() => {
    const errors = validate();
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      return;
    }
    setFieldErrors({});
    handleProfile(formData);
  }, [formData, handleProfile]);

  const handleCancel = useCallback(() => {
    setFieldErrors({});
    setShowOldPassword(false);
    setShowNewPassword(false);
    setFormData({
      first_name: profile?.first_name || "",
      last_name: profile?.last_name || "",
      email_or_phone: profile?.email_or_phone || "",
      old_password: "",
      new_password: "",
    });
    resetState();
  }, [profile, resetState]);

  if (loading) {
    return (
      <div
        className="container d-flex justify-content-center align-items-center"
        style={{ minHeight: "300px" }}
      >
        <div className="spinner-border text-success" role="status" />
      </div>
    );
  }

  return (
    <div className="container d-flex justify-content-center">
      <div className="details-card">
        <div className="header-icon-container">
          <div className="header-icon-circle">
            <UserRoundPen size={38} strokeWidth={2} />
          </div>
        </div>

        <div className="card-header">
          <h2 className="card-title">تعديل الملف الشخصي</h2>
        </div>

        <div className="row g-2 mb-3">
          <div className="col-6">
            <div className="mb-1">
              <label className="form-label">الاسم الأول</label>
              <input
                type="text"
                name="first_name"
                className={`form-control ${fieldErrors.first_name ? "is-invalid" : ""}`}
                value={formData.first_name}
                onChange={handleInputChange}
                placeholder="مثال: أحمد"
              />
              {fieldErrors.first_name && (
                <div className="invalid-feedback">{fieldErrors.first_name}</div>
              )}
            </div>
          </div>

          <div className="col-6">
            <div className="mb-1">
              <label className="form-label">الاسم الأخير</label>
              <input
                type="text"
                name="last_name"
                className={`form-control ${fieldErrors.last_name ? "is-invalid" : ""}`}
                value={formData.last_name}
                onChange={handleInputChange}
                placeholder="مثال: محمد"
              />
              {fieldErrors.last_name && (
                <div className="invalid-feedback">{fieldErrors.last_name}</div>
              )}
            </div>
          </div>

          <div className="col-12">
            <div className="mb-1">
              <label className="form-label">
                البريد الإلكتروني أو رقم الهاتف
              </label>
              <input
                type="text"
                name="email_or_phone"
                className={`form-control ${fieldErrors.email_or_phone ? "is-invalid" : ""}`}
                value={formData.email_or_phone}
                onChange={handleInputChange}
                placeholder="example@email.com أو 249xxxxxxxxx+"
              />
              {fieldErrors.email_or_phone && (
                <div className="invalid-feedback">
                  {fieldErrors.email_or_phone}
                </div>
              )}
            </div>
          </div>

          <div className="col-12">
            <div className="mb-1">
              <label className="form-label">كلمة المرور القديمة</label>
              <div className="position-relative">
                <input
                  type={showOldPassword ? "text" : "password"}
                  name="old_password"
                  className={`form-control ${fieldErrors.old_password ? "is-invalid" : ""}`}
                  placeholder="أدخل كلمة المرور القديمة"
                  onChange={handleInputChange}
                />
                <span
                  onClick={() => setShowOldPassword((prev) => !prev)}
                  style={{
                    position: "absolute",
                    left: "10px",
                    top: fieldErrors.old_password ? "35%" : "50%",
                    transform: "translateY(-50%)",
                    cursor: "pointer",
                    color: "#6c757d",
                  }}
                >
                  {showOldPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </span>
                {fieldErrors.old_password && (
                  <div className="invalid-feedback">
                    {fieldErrors.old_password}
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="col-12">
            <div className="mb-1">
              <label className="form-label">كلمة المرور الجديدة</label>
              <div className="position-relative">
                <input
                  type={showNewPassword ? "text" : "password"}
                  name="new_password"
                  className={`form-control ${fieldErrors.new_password ? "is-invalid" : ""}`}
                  placeholder="أدخل كلمة المرور الجديدة"
                  onChange={handleInputChange}
                />
                <span
                  onClick={() => setShowNewPassword((prev) => !prev)}
                  style={{
                    position: "absolute",
                    left: "10px",
                    top: fieldErrors.new_password ? "35%" : "50%",
                    transform: "translateY(-50%)",
                    cursor: "pointer",
                    color: "#6c757d",
                  }}
                >
                  {showNewPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </span>
                {fieldErrors.new_password && (
                  <div className="invalid-feedback">
                    {fieldErrors.new_password}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="alert alert-danger text-center" role="alert">
            {error}
          </div>
        )}

        <div className="actions">
          <button
            className="btn btn-success"
            onClick={handleSubmit}
            disabled={updating}
          >
            {updating ? (
              <span
                className="spinner-border spinner-border-sm"
                role="status"
              />
            ) : (
              "تحديث"
            )}
          </button>
          <button className="btn btn-cancel" onClick={handleCancel}>
            الغاء
          </button>
        </div>

        {successMessage && (
          <div className="success-message text-success">
            {successMessage}
            <BadgeCheck size={25} strokeWidth={2.5} color="#198754" />
          </div>
        )}
      </div>
    </div>
  );
}
