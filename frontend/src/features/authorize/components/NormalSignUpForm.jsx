export function NormalSignUpForm({ role, userData, handleDataChange }) {
  const handlefirstName = (e) => {
    handleDataChange({ first_name: e.target.value });
  };

  const handleLastName = (e) => {
    handleDataChange({ last_name: e.target.value });
  };

  const handleEmailOrPhoneChange = (e) => {
    handleDataChange({ email_or_phone: e.target.value });
  };

  return (
    <>
      <div id="userNameFields" className="row g-3 mb-3">
        <div className="col-6 text-end">
          <label className="form-label">الاسم الأول</label>
          <input
            type="text"
            name="first_name"
            className="form-control"
            required={role === "user"}
            value={userData.first_name}
            onChange={handlefirstName}
          />
          <div className="invalid-feedback">يرجى إدخال الاسم الأول</div>
        </div>
        <div className="col-6 text-end">
          <label className="form-label">اسم العائلة</label>
          <input
            type="text"
            name="last_name"
            className="form-control"
            required={role === "user"}
            value={userData.last_name}
            onChange={handleLastName}
          />
          <div className="invalid-feedback">يرجى إدخال اسم العائلة</div>
        </div>
      </div>

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
    </>
  );
}
