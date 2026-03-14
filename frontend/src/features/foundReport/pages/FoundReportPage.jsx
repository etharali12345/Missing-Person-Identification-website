import { useState } from "react";
import { useFoundReport } from "../hooks/useFoundReport";
import { FoundReportFrom } from "../components/Form/FoundReportForm";
import "../../../styles/uploadForm.css";

export function FoundReportPage() {
  const [showForm, setShowForm] = useState(true);
  const { submitReport, validateMatch, loading, error, result } =
    useFoundReport();

  return (
    <div className="container text-center my-3">
      <h6>قبل رفع الصورة الرجاء اقراء التعليمات التالية</h6>
      <div className="row gy-5 align-items-stretch justify-content-center">
        {showForm && (
          <div className="col-12 px-5 col-md-6 center-flex align-items-stretch">
            <FoundReportFrom
              submitReport={submitReport}
              error={error}
              loading={loading}
            />
          </div>
        )}
      </div>
    </div>
  );
}
