import { useState } from "react";
import { ImagePreview } from "../../../components/shared/ImagePreview";
import { MissingReportFields } from "./MissingReportFields";

export function MissingReportForm({ submitReport, error }) {
  const [validated, setValidated] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [uploadData, setUploadData] = useState({
    image: null,
    name: "",
    age: "",
    gender: "",
    last_seen_data: "",
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
    formData.append("image", uploadData.image);
    formData.append("name", uploadData.name);
    formData.append("gender", uploadData.gender);
    formData.append("last_seen_data", uploadData.last_seen_data);
    formData.append("last_seen_location", uploadData.last_seen_location);
    formData.append("phone_number1", uploadData.phone_number1);
    formData.append("phone_number2", uploadData.phone_number2);

    await submitReport(formData);
    setSubmitted(true);
  };

  return (
    <form
      noValidate
      onSubmit={handleSubmit}
      className={`needs-validation ${validated && !submitted ? "was-validated" : ""} center-flex flex-column w-100`}
    >
      <ImagePreview image={uploadData.image} setImage={handleImageChange} />
      <div className="glass-reportCard">
        <h6>ادخل بيانات الشخص المفقود</h6>
        <MissingReportFields
          handleInputChange={handleInputChange}
          submitted={submitted}
          validated={validated}
        />
        {validated && !uploadData.image && <p>يرجى ارفاق صورة الشخص المفقود</p>}
        {error && (
          <div className="alert alert-danger center-flex p-3" role="alert">
            {error}
          </div>
        )}
        <button type="submit" className="btn btn-success w-100">
          ارسال
        </button>
      </div>
    </form>
  );
}
