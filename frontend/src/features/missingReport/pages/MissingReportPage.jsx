import { useMissingReport } from "../hooks/useMissingReport";
import { MissingReportForm } from "../components/MissingReportForm";
import "../../../styles/uploadForm.css";

export function MissingReportPage() {
  const { submitReport, validateMatch, loading, error, result } =
    useMissingReport();

  return (
    <div className="container text-center my-3">
      <h6>قبل رفع الصورة الرجاء اقراء التعليمات التالية</h6>
      <div className="row gy-5 align-items-stretch justify-content-center">
        <div className="col-12 px-5 col-md-6 center-flex">
          <MissingReportForm submitReport={submitReport} error={error} />
        </div>
      </div>
    </div>
  );
}
