import { useEffect, useCallback, useState } from "react";
import { UserRoundPen, BadgeCheck, Eye, EyeOff } from "lucide-react";
import { useProfile } from "../hooks/useProfile";
import "./profilePage.css";

export function ProfilePage() {
  const {
    profile,
    loading,
    updating,
    updatingPassword,
    error,
    passwordError,
    successMessage,
    passwordSuccessMessage,
    handleProfile,
    handlePassword,
    resetState,
  } = useProfile();

  const [showOldPassword, setShowOldPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [infoErrors, setInfoErrors] = useState({});
  const [passwordErrors, setPasswordErrors] = useState({});

  const [infoData, setInfoData] = useState({
    first_name: "",
    last_name: "",
    email_or_phone: "",
  });

  const [passwordData, setPasswordData] = useState({
    old_password: "",
    new_password: "",
  });

  useEffect(() => {
    if (profile) {
      setInfoData({
        first_name: profile.first_name || "",
        last_name: profile.last_name || "",
        email_or_phone: profile.email_or_phone || "",
      });
    }
  }, [profile]);

  useEffect(() => {
    if (passwordSuccessMessage) {
      setPasswordData({ old_password: "", new_password: "" });
    }
  }, [passwordSuccessMessage]);

  const handleInfoChange = (e) => {
    const { name, value } = e.target;
    setInfoData((prev) => ({ ...prev, [name]: value }));
    setInfoErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData((prev) => ({ ...prev, [name]: value }));
    setPasswordErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const validateInfo = () => {
    const errors = {};
    if (!infoData.first_name.trim())
      errors.first_name = "يرجى إدخال الاسم الأول";
    if (!infoData.last_name.trim())
      errors.last_name = "يرجى إدخال الاسم الأخير";
    if (!infoData.email_or_phone.trim())
      errors.email_or_phone = "يرجى إدخال البريد الإلكتروني أو رقم الهاتف";
    return errors;
  };

  const validatePassword = () => {
    const errors = {};
    if (!passwordData.old_password)
      errors.old_password = "يرجى إدخال كلمة المرور القديمة";
    if (!passwordData.new_password)
      errors.new_password = "يرجى إدخال كلمة المرور الجديدة";
    else if (passwordData.new_password.length < 6)
      errors.new_password = "كلمة المرور يجب أن تكون 6 أحرف على الأقل";
    return errors;
  };

  const isChangingPassword = !!(
    passwordData.old_password || passwordData.new_password
  );

  const isInfoChanged =
    infoData.first_name !== (profile?.first_name || "") ||
    infoData.last_name !== (profile?.last_name || "") ||
    infoData.email_or_phone !== (profile?.email_or_phone || "");

  const handleSubmit = useCallback(() => {
    const infoErrs = isInfoChanged ? validateInfo() : {};
    const passErrs = isChangingPassword ? validatePassword() : {};

    if (Object.keys(infoErrs).length > 0) setInfoErrors(infoErrs);
    if (Object.keys(passErrs).length > 0) setPasswordErrors(passErrs);
    if (Object.keys(infoErrs).length > 0 || Object.keys(passErrs).length > 0)
      return;

    if (!isInfoChanged && !isChangingPassword) return;

    setInfoErrors({});
    setPasswordErrors({});
    if (isInfoChanged) handleProfile(infoData);
    if (isChangingPassword) handlePassword(passwordData);
  }, [
    infoData,
    passwordData,
    isInfoChanged,
    isChangingPassword,
    handleProfile,
    handlePassword,
  ]);

  const handleCancel = useCallback(() => {
    setInfoErrors({});
    setPasswordErrors({});
    setShowOldPassword(false);
    setShowNewPassword(false);
    setInfoData({
      first_name: profile?.first_name || "",
      last_name: profile?.last_name || "",
      email_or_phone: profile?.email_or_phone || "",
    });
    setPasswordData({ old_password: "", new_password: "" });
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

        {/* ── Personal Info Section ── */}
        <div className="row g-2 mb-3">
          <div className="col-6">
            <div className="mb-1">
              <label className="form-label">الاسم الأول</label>
              <input
                type="text"
                name="first_name"
                className={`form-control ${infoErrors.first_name ? "is-invalid" : ""}`}
                value={infoData.first_name}
                onChange={handleInfoChange}
                placeholder="مثال: أحمد"
              />
              {infoErrors.first_name && (
                <div className="invalid-feedback">{infoErrors.first_name}</div>
              )}
            </div>
          </div>

          <div className="col-6">
            <div className="mb-1">
              <label className="form-label">الاسم الأخير</label>
              <input
                type="text"
                name="last_name"
                className={`form-control ${infoErrors.last_name ? "is-invalid" : ""}`}
                value={infoData.last_name}
                onChange={handleInfoChange}
                placeholder="مثال: محمد"
              />
              {infoErrors.last_name && (
                <div className="invalid-feedback">{infoErrors.last_name}</div>
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
                className={`form-control ${infoErrors.email_or_phone ? "is-invalid" : ""}`}
                value={infoData.email_or_phone}
                onChange={handleInfoChange}
                placeholder="example@email.com أو 249xxxxxxxxx+"
              />
              {infoErrors.email_or_phone && (
                <div className="invalid-feedback">
                  {infoErrors.email_or_phone}
                </div>
              )}
            </div>
          </div>
        </div>

        {error && (
          <div className="alert alert-danger text-center" role="alert">
            {error}
          </div>
        )}

        {/* ── Divider with label ── */}
        <div
          className="d-flex align-items-center my-4"
          style={{ gap: "0.75rem" }}
        >
          <hr style={{ flex: 1, margin: 0 }} />
          <span
            style={{
              color: "#6c757d",
              fontSize: "0.85rem",
              whiteSpace: "nowrap",
            }}
          >
            تغيير كلمة المرور
          </span>
          <hr style={{ flex: 1, margin: 0 }} />
        </div>

        {/* ── Password Section ── */}
        <div className="row g-2 mb-3">
          <div className="col-12">
            <div className="mb-1">
              <label className="form-label">كلمة المرور القديمة</label>
              <div className="position-relative">
                <input
                  type={showOldPassword ? "text" : "password"}
                  name="old_password"
                  value={passwordData.old_password}
                  className={`form-control ${passwordErrors.old_password ? "is-invalid" : ""}`}
                  placeholder="أدخل كلمة المرور القديمة"
                  onChange={handlePasswordChange}
                />
                <span
                  onClick={() => setShowOldPassword((prev) => !prev)}
                  style={{
                    position: "absolute",
                    left: "10px",
                    top: passwordErrors.old_password ? "35%" : "50%",
                    transform: "translateY(-50%)",
                    cursor: "pointer",
                    color: "#6c757d",
                  }}
                >
                  {showOldPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </span>
                {passwordErrors.old_password && (
                  <div className="invalid-feedback">
                    {passwordErrors.old_password}
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
                  value={passwordData.new_password}
                  className={`form-control ${passwordErrors.new_password ? "is-invalid" : ""}`}
                  placeholder="أدخل كلمة المرور الجديدة"
                  onChange={handlePasswordChange}
                />
                <span
                  onClick={() => setShowNewPassword((prev) => !prev)}
                  style={{
                    position: "absolute",
                    left: "10px",
                    top: passwordErrors.new_password ? "35%" : "50%",
                    transform: "translateY(-50%)",
                    cursor: "pointer",
                    color: "#6c757d",
                  }}
                >
                  {showNewPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </span>
                {passwordErrors.new_password && (
                  <div className="invalid-feedback">
                    {passwordErrors.new_password}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {passwordError && (
          <div className="alert alert-danger text-center" role="alert">
            {passwordError}
          </div>
        )}

        {(successMessage || passwordSuccessMessage) && (
          <div className="success-message text-success pt-2 pb-2">
            {passwordSuccessMessage || successMessage}
            <BadgeCheck size={25} strokeWidth={2.5} color="#198754" />
          </div>
        )}

        {/* ── Single action row ── */}
        <div className="actions">
          <button
            className="btn btn-success"
            onClick={handleSubmit}
            disabled={updating || updatingPassword}
          >
            {updating || updatingPassword ? (
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
      </div>
    </div>
  );
}
