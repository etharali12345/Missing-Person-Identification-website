import { useState } from "react";
import { ImagePreview } from "../../../../components/shared/ImagePreview";
import { FoundFormFields } from "./FoundFormFields";

export function FoundReportForm({ submitReport, error, loading }) {
  const [validated, setValidated] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [uploadData, setUploadData] = useState({
    image: null,
    full_name: "",
    approximate_age: "",
    gender: "",
    health_status: "",
    found_date: "",
    found_location: "",
    phone_number1: "",
    phone_number2: "",
  });

  const handleFormChange = (data) => {
    setUploadData((prev) => ({ ...prev, ...data }));
  };

  const handleInputChange = (e) => {
    handleFormChange({ [e.target.name]: e.target.value });
  };

  const handleImageChange = (img) => {
    handleFormChange({ image: img });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    if (!form.checkValidity() || !uploadData.image) {
      event.stopPropagation();
      setValidated(true);
      return;
    }
    setValidated(true);
    const formData = new FormData();

    formData.append("image_path", uploadData.image);
    formData.append("phone_number1", uploadData.phone_number1);
    formData.append("phone_number2", uploadData.phone_number2);

    if (uploadData.full_name)
      formData.append("full_name", uploadData.full_name);
    if (uploadData.approximate_age)
      formData.append("approximate_age", uploadData.approximate_age);
    if (uploadData.gender) formData.append("gender", uploadData.gender);
    if (uploadData.health_status)
      formData.append("health_status", uploadData.health_status);
    if (uploadData.found_date)
      formData.append("found_date", uploadData.found_date);
    if (uploadData.found_location)
      formData.append("found_location", uploadData.found_location);

    try {
      await submitReport(formData);
      setSubmitted(true);
    } catch (e) {
      setSubmitted(false);
    }
  };

  return (
    <form
      noValidate
      onSubmit={handleSubmit}
      className={`needs-validation ${validated && !submitted ? "was-validated" : ""} center-flex flex-column w-100`}
    >
      <ImagePreview
        image={uploadData.image}
        setImage={handleImageChange}
        isMissing={false}
      />

      <div className="glass-reportCard d-flex flex-column">
        <h6>ادخل بيانات الشخص المعثور عليه</h6>
        <FoundFormFields
          handleInputChange={handleInputChange}
          submitted={submitted}
          validated={validated}
        />
        {validated && !uploadData.image && (
          <p className="text-center text-danger">
            يرجى إرفاق صورة الشخص المعثور عليه
          </p>
        )}
        {error && (
          <div
            className="alert alert-danger center-flex p-3 text-center"
            role="alert"
          >
            {error}
          </div>
        )}
        <div className="mt-auto">
          <button
            type="submit"
            className="btn btn-success w-100 mt-auto"
            disabled={submitted || loading}
          >
            ارسال
          </button>
        </div>
      </div>
    </form>
  );
}
