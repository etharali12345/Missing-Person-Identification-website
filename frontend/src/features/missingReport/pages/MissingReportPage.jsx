import { useState } from "react";
import { useMissingReport } from "../hooks/useMissingReport";
import { MissingReportForm } from "../components/MissingReportForm";
import { MissingReportResult } from "../components/MissingReportResult";
import "../../../styles/uploadForm.css";

export function MissingReportPage() {
  const [showForm, setShowForm] = useState(true);
  const { submitReport, validateMatch, loading, error, result } =
    useMissingReport();

  return (
    <div className="container text-center my-3">
      <h6>قبل رفع الصورة الرجاء اقراء التعليمات التالية</h6>
      <div className="row gy-5 align-items-stretch justify-content-center">
        {showForm && (
          <div className="col-12 px-5 col-md-6 center-flex align-items-stretch">
            <MissingReportForm
              submitReport={submitReport}
              error={error}
              loading={loading}
            />
          </div>
        )}
        {result && (
          <div className="col-12 px-5 col-md-6 center-flex align-items-stretch">
            <MissingReportResult
              result={result}
              setShowForm={setShowForm}
              validateMatch={validateMatch}
            />
          </div>
        )}
      </div>
    </div>
  );
}
