import { useState } from "react";
import { ImagePreview } from "../../../../components/shared/ImagePreview";
import { MissingFormFields } from "./MissingFormFields";

export function MissingReportForm({ submitReport, error, loading }) {
  const [validated, setValidated] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [uploadData, setUploadData] = useState({
    image: null,
    name: "",
    age: "",
    gender: "",
    last_seen_date: "",
    last_seen_location: "",
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
    formData.append("full_name", uploadData.name);
    formData.append("gender", uploadData.gender);
    formData.append("age", uploadData.age);
    formData.append("phone_number1", uploadData.phone_number1);
    formData.append("phone_number2", uploadData.phone_number2);

    if (uploadData.last_seen_date) {
      formData.append("last_seen_date", uploadData.last_seen_date);
    }
    if (uploadData.last_seen_location) {
      formData.append("last_seen_location", uploadData.last_seen_location);
    }
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
      <ImagePreview image={uploadData.image} setImage={handleImageChange} />
      <div className="glass-reportCard d-flex flex-column">
        <h6>ادخل بيانات الشخص المفقود</h6>
        <MissingFormFields
          handleInputChange={handleInputChange}
          submitted={submitted}
          validated={validated}
        />
        {validated && !uploadData.image && (
          <p className="text-center text-danger">
            يرجى إرفاق صورة الشخص المفقود
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
            className="btn btn-success w-100"
            disabled={submitted || loading}
          >
            {loading ? (
              <>
                <span
                  className="spinner-border spinner-border-sm slow-spinner me-2"
                  role="status"
                  aria-hidden="true"
                ></span>
              </>
            ) : (
              "إرسال"
            )}
          </button>
        </div>
      </div>
    </form>
  );
}
