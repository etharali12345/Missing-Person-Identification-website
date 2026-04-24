import { useState, useEffect } from "react";
import { BaseModal } from "../../../components/shared/list/BaseModal";
import "./updateMissingModal.css";

export function UpdateMissingModal({ show, profile, onConfirm, onCancel }) {
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (profile) {
      setFormData({
        full_name: profile.full_name || "",
        age: profile.age || "",
        gender: profile.gender || "",
        last_seen_date: profile.last_seen_date || "",
        last_seen_location: profile.last_seen_location || "",
        phone_number1: profile.phone_number1 || "",
        phone_number2: profile.phone_number2 || "",
      });
      setErrors({});
    }
  }, [profile, show]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.full_name.trim())
      newErrors.full_name = "يرجى إدخال اسم المفقود ";
    if (!formData.age || formData.age <= 0 || formData.age > 120)
      newErrors.age = "يرجى إدخال عمر صحيح بين 1 و 120";

    const phoneRegex = /^\+?[0-9]{7,15}$/;
    if (!phoneRegex.test(formData.phone_number1.trim()))
      newErrors.phone_number1 = "يرجى إدخال رقم هاتف صحيح";
    if (!phoneRegex.test(formData.phone_number2.trim()))
      newErrors.phone_number2 = "يرجى إدخال رقم هاتف صحيح";

    return newErrors;
  };

  const handleSubmit = () => {
    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    const cleanedData = {
      full_name: formData.full_name,
      age: formData.age,
      gender: formData.gender,
      phone_number1: formData.phone_number1,
      phone_number2: formData.phone_number2,
      ...(formData.last_seen_date && {
        last_seen_date: formData.last_seen_date,
      }),
      ...(formData.last_seen_location && {
        last_seen_location: formData.last_seen_location,
      }),
    };

    onConfirm(profile.id, cleanedData);
  };

  const handleCancel = () => {
    setFormData({
      full_name: profile.full_name || "",
      age: profile.age || "",
      gender: profile.gender || "",
      last_seen_date: profile.last_seen_date || "",
      last_seen_location: profile.last_seen_location || "",
      phone_number1: profile.phone_number1 || "",
      phone_number2: profile.phone_number2 || "",
    });
    setErrors({});
    onCancel();
  };

  return (
    <BaseModal
      show={show}
      title="تعديل البلاغ"
      onCancel={handleCancel}
      customClass="update-modal"
      footer={
        <>
          <button className="btn btn-primary" onClick={handleSubmit}>
            تحديث
          </button>
          <button className="btn btn-secondary" onClick={handleCancel}>
            إلغاء
          </button>
        </>
      }
    >
      <div className="d-flex justify-content-center update-image">
        <img
          src={profile.image_path}
          alt={profile.full_name}
          style={{ width: "200px" }}
        />
      </div>
      <div className="row g-2 px-3 py-4 justify-content-center update-form">
        <h5 className="text-center">معلومات المفقود</h5>

        <div className="col-9">
          <label className="form-label">الاسم</label>
          <input
            className={`form-control text-end ${errors.full_name ? "is-invalid" : ""}`}
            name="full_name"
            placeholder="الاسم الكامل"
            required
            value={formData.full_name}
            onChange={handleChange}
          />
          {errors.full_name && (
            <div className="invalid-feedback">{errors.full_name}</div>
          )}
        </div>

        <div className="col-3">
          <label className="form-label">العمر</label>
          <input
            className={`form-control text-end ${errors.age ? "is-invalid" : ""}`}
            name="age"
            type="number"
            placeholder="العمر"
            required
            value={formData.age}
            onChange={handleChange}
          />
          {errors.age && <div className="invalid-feedback">{errors.age}</div>}
        </div>

        <div className="col-6">
          <label className="form-label">الجنس</label>
          <select
            className="form-select text-end"
            name="gender"
            required
            value={formData.gender}
            onChange={handleChange}
          >
            <option value="male">ذكر</option>
            <option value="female">أنثى</option>
          </select>
        </div>

        <div className="col-6">
          <label className="form-label">تاريخ اخر مشاهدة</label>
          <input
            className="form-control text-end"
            name="last_seen_date"
            type="date"
            value={formData.last_seen_date}
            onChange={handleChange}
          />
        </div>

        <div className="col-12">
          <label className="form-label">آخر موقع مشاهدة</label>
          <input
            className="form-control text-end"
            name="last_seen_location"
            placeholder="آخر موقع"
            value={formData.last_seen_location}
            onChange={handleChange}
          />
        </div>

        <div className="col-6">
          <label className="form-label">رقم الهاتفك للتواصل</label>
          <input
            className={`form-control text-end ${errors.phone_number1 ? "is-invalid" : ""}`}
            name="phone_number1"
            placeholder="رقم الهاتف 1"
            value={formData.phone_number1}
            onChange={handleChange}
          />
          {errors.phone_number1 && (
            <div className="invalid-feedback">{errors.phone_number1}</div>
          )}
        </div>

        <div className="col-6">
          <label className="form-label">رقم الهاتف اخر</label>
          <input
            className={`form-control text-end ${errors.phone_number2 ? "is-invalid" : ""}`}
            name="phone_number2"
            placeholder="رقم الهاتف 2"
            value={formData.phone_number2}
            onChange={handleChange}
          />
          {errors.phone_number2 && (
            <div className="invalid-feedback">{errors.phone_number2}</div>
          )}
        </div>
      </div>
    </BaseModal>
  );
}
