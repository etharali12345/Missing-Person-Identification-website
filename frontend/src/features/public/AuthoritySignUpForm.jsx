import { useState } from "react";
import { MapPin, UploadCloud, FolderCheck } from "lucide-react";

export function AuthoritySignUpForm({ role, userData, handleDataChange }) {
  const handleDocumentChange = (e) => {
    handleDataChange({ document: e.target.files[0] });
  };

  const handleAuthorityTypeChange = (e) => {
    handleDataChange({ authority_type: e.target.value });
  };

  const handleAuthorityNameChange = (e) => {
    handleDataChange({ authority_name: e.target.value });
  };

  const handleLocationChange = (e) => {
    handleDataChange({ location: e.target.value });
  };

  const handlelicenseChange = (e) => {
    handleDataChange({ license_number: e.target.value });
  };

  return (
    <div id="authorityFields">
      <div className="mb-3 text-end">
        <label className="form-label">تصنيف الجهة</label>
        <div className="row g-2">
          <div className="col-6">
            <label
              className={`entity-selector h-100 ${userData.authority_type === "organization" ? "active" : ""}`}
              id="orgLabel"
            >
              <input
                type="radio"
                name="authorityType"
                value="organization"
                className="d-none"
                onChange={handleAuthorityTypeChange}
              />
              <span className="custom-radio-circle"></span>
              <span className="small">منظمة</span>
            </label>
          </div>
          <div className="col-6">
            <label
              className={`entity-selector h-100 ${userData.authority_type === "service" ? "active" : ""}`}
              id="serviceLabel"
            >
              <input
                type="radio"
                name="authorityType"
                value="service"
                className="d-none"
                onChange={handleAuthorityTypeChange}
              />
              <span className="custom-radio-circle"></span>
              <span className="small">جهة خدمية</span>
            </label>
          </div>
        </div>
      </div>

      <div className="mb-3 text-end">
        <label className="form-label">اسم الجهة</label>
        <input
          type="text"
          name="authority_name"
          className="form-control"
          required={role === "authority"}
          value={userData.authority_name}
          onChange={handleAuthorityNameChange}
        />
        <div className="invalid-feedback">يرجى إدخال اسم الجهة</div>
      </div>

      <div className="mb-3 text-end">
        <label className="form-label">موقع المقر</label>
        <div className="location-input-group">
          <span className="location-icon">
            <MapPin size={18} />
          </span>
          <input
            type="text"
            name="location"
            placeholder="المدينة، الحي"
            className="form-control"
            required={role === "authority"}
            value={userData.location}
            onChange={handleLocationChange}
          />
        </div>
        <div className="invalid-feedback">يرجى إدخال موقع المقر</div>
      </div>

      {userData.authority_type === "organization" && (
        <div id="licenseField" className="mb-3 text-end">
          <label className="form-label">رقم تسجيل المنظمة</label>
          <input
            type="text"
            name="license_number"
            className="form-control"
            required={userData.authority_type === "organization"}
            value={userData.license_number}
            onChange={handlelicenseChange}
          />
          <div className="invalid-feedback">يرجى إدخال رقم تسجيل المنظمة</div>
        </div>
      )}

      <div className="mb-3 text-end">
        <label className="form-label">الوثائق الثبوتية</label>

        <label className="upload-area d-block text-center" htmlFor="fileUpload">
          {userData.document ? (
            <>
              <FolderCheck
                className="text-secondary mb-2"
                size={30}
                color="#198653"
              />
              <div className="small text-success">{userData.document.name}</div>
            </>
          ) : (
            <>
              <UploadCloud className="text-secondary mb-2" size={32} />
              <div className="small text-secondary">ارفع وثيقة الإثبات</div>
            </>
          )}
        </label>

        <input
          id="fileUpload"
          type="file"
          name="document"
          className="d-none"
          required={role === "authority"}
          onChange={handleDocumentChange}
        />
        <div className="invalid-feedback">
          يرجى إرفاق وثيقة رسمية تثبت اعتماد الجهة
        </div>
      </div>
    </div>
  );
}
