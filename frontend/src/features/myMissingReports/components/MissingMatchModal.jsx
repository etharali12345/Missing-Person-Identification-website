import { BaseModal } from "../../../components/shared/list/BaseModal";
import { ImageShow } from "../../../components/shared/ImageShow";
import { CircularProgress } from "../../../components/shared/CircularProgress";
import { LinearProgress } from "../../../components/shared/LinearProgress";
import { MissingDetails } from "../../missingReport/components/result/MissingDetails";
import "../../../components/shared/ReportResult.css";

export function MissingMatchModal({ show, details, loading, onCancel }) {
  const genderLabel = details?.gender === "male" ? "ذكر" : "أنثى";
  const percentage = details?.percentage
    ? `${Math.round(details.percentage * 100)}%`
    : null;

  return (
    <BaseModal
      show={show}
      title="تفاصيل التطابق"
      onCancel={onCancel}
      customClass="custome-modal"
      footer={
        <button className="btn btn-secondary" onClick={onCancel}>
          إغلاق
        </button>
      }
    >
      {loading && (
        <div className="text-center py-4">
          <div className="spinner-border text-primary" role="status" />
          <p className="mt-2">جاري التحميل...</p>
        </div>
      )}

      {!loading && details && (
        <>
          <div className="d-flex justify-content-center custome-image">
            <img src={details.image_path} alt={details.full_name} />
          </div>
          <div className="px-3 py-4 custome-form">
            <h5 className="text-center">معلومات المعثور عليه</h5>

            <p className="text-center mb-0">نسبة التطابق:</p>
            <p className="percentage">{percentage}</p>
            <LinearProgress value={details.percentage} color="green" />
            <MissingDetails details={details} />
          </div>
        </>
      )}
    </BaseModal>
  );
}
