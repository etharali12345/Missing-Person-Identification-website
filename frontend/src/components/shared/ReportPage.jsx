import { useState } from "react";
import { ReportResult } from "./ReportResult";
import "./ReportPage.css";

export function ReportPage({
  useReport,
  FormComponent,
  DetailsComponent,
  noMatchMessage,
}) {
  const [showForm, setShowForm] = useState(true);
  const { submitReport, validateUncertain, loading, error, result } =
    useReport();

  return (
    <div className="container text-center my-3">
      <h6>قبل رفع الصورة الرجاء اقراء التعليمات التالية</h6>
      <div className="row gy-5 align-items-stretch justify-content-center">
        {showForm && (
          <div className="col-12 px-5 col-md-6 center-flex align-items-stretch">
            <FormComponent
              submitReport={submitReport}
              error={error}
              loading={loading}
            />
          </div>
        )}
        {result && (
          <div className="col-12 px-5 col-md-6 center-flex align-items-stretch">
            <ReportResult
              result={result}
              setShowForm={setShowForm}
              noMatchMessage={noMatchMessage}
              DetailsComponent={DetailsComponent}
              validateUncertain={validateUncertain}
            />
          </div>
        )}
      </div>
    </div>
  );
}
