import { useState, useEffect, useRef } from "react";
import { BaseModal } from "../../../components/shared/list/BaseModal";

export function UpdateFoundModal({
  show,
  profile,
  onConfirm,
  onCancel,
  updateError,
}) {
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});
  const errorRef = useRef(null);

  useEffect(() => {
    if (profile) {
      setFormData({
        full_name: profile.full_name || "",
        approximate_age: profile.approximate_age || "",
        gender: profile.gender || "",
        health_status: profile.health_status || "",
        found_date: profile.found_date || "",
        found_location: profile.found_location || "",
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
      gender: formData.gender,
      phone_number1: formData.phone_number1,
      phone_number2: formData.phone_number2,

      ...(formData.full_name && {
        full_name: formData.full_name,
      }),
      ...(formData.approximate_age && {
        approximate_age: formData.approximate_age,
      }),
      ...(formData.health_status && {
        health_status: formData.health_status,
      }),
      ...(formData.found_date && {
        found_date: formData.found_date,
      }),
      ...(formData.found_location && {
        found_location: formData.found_location,
      }),
      ...(formData.found_date && {
        found_date: formData.found_date,
      }),
      ...(formData.found_location && {
        found_location: formData.found_location,
      }),
    };

    onConfirm(profile.id, cleanedData);
  };

  const handleCancel = () => {
    setFormData({
      full_name: profile.full_name || "",
      approximate_age: profile.approximate_age || "",
      gender: profile.gender || "",
      health_status: profile.health_status || "",
      found_date: profile.found_date || "",
      found_location: profile.found_location || "",
      phone_number1: profile.phone_number1 || "",
      phone_number2: profile.phone_number2 || "",
    });
    setErrors({});
    onCancel();
  };

  useEffect(() => {
    if (updateError && errorRef.current) {
      errorRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [updateError]);

  return (
    <BaseModal
      show={show}
      title="تعديل بلاغ المعثور عليه"
      onCancel={handleCancel}
      customClass="custome-modal"
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
      <div className="d-flex justify-content-center custome-image">
        <img src={profile.image_path} alt={profile.full_name} />
      </div>

      <div className=" px-3 py-4 custome-form">
        <h5 className="text-center">معلومات المعثور عليه</h5>

        <div className="row g-2 justify-content-center">
          <div className="col-9">
            <label className="form-label">الاسم</label>
            <input
              className={"form-control text-end"}
              name="full_name"
              placeholder="الاسم الكامل"
              value={formData.full_name}
              onChange={handleChange}
            />
          </div>

          <div className="col-3">
            <label className="form-label"> العمر</label>
            <input
              className={"form-control text-end "}
              name="approximate_age"
              type="number"
              placeholder="العمر"
              required
              value={formData.approximate_age}
              onChange={handleChange}
            />
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
            <label className="form-label">تاريخ العثور</label>
            <input
              className="form-control text-end"
              name="found_date"
              type="date"
              value={formData.found_date}
              onChange={handleChange}
            />
          </div>

          <div className="col-12">
            <label className="form-label">الحالة الصحية</label>
            <input
              className="form-control text-end"
              name="health_status"
              placeholder="الحالة الصحية"
              value={formData.health_status}
              onChange={handleChange}
            />
          </div>

          <div className="col-12">
            <label className="form-label"> موقع العثور</label>
            <input
              className="form-control text-end"
              name="found_location"
              placeholder="موقع العثور"
              value={formData.found_location}
              onChange={handleChange}
            />
          </div>

          <div className="col-6">
            <label className="form-label">رقم هاتفك للتواصل</label>
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
            <label className="form-label">رقم هاتف اخر</label>
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
      </div>
      {updateError && (
        <div className="col-12" ref={errorRef}>
          <div className="alert alert-danger text-center py-2">
            {updateError}
          </div>
        </div>
      )}
    </BaseModal>
  );
}
