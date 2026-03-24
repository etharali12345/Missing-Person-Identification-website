export function NormalSignUpForm({ role, userData, handleDataChange }) {
  const handlefirstName = (e) => {
    handleDataChange({ first_name: e.target.value });
  };

  const handleLastName = (e) => {
    handleDataChange({ last_name: e.target.value });
  };

  return (
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
  );
}
