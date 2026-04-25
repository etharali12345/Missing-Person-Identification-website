import { BaseModal } from "../../../components/shared/list/BaseModal";

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
      customClass="match-modal"
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
          <div className="d-flex justify-content-center">
            <img
              src={details.image_path}
              alt={details.full_name}
              style={{ width: "200px", borderRadius: "10px" }}
            />
          </div>

          {percentage && (
            <div className="text-center mt-2">
              <span className="badge bg-success fs-6">
                نسبة التطابق: {percentage}
              </span>
            </div>
          )}

          <div className="row g-2 px-3 py-3 text-end">
            <h5 className="text-center">معلومات الشخص المعثور عليه</h5>

            <div className="col-9">
              <label className="form-label fw-bold">الاسم</label>
              <p className="form-control">{details.full_name}</p>
            </div>

            <div className="col-3">
              <label className="form-label fw-bold">العمر التقريبي</label>
              <p className="form-control">{details.approximate_age}</p>
            </div>

            <div className="col-6">
              <label className="form-label fw-bold">الجنس</label>
              <p className="form-control">{genderLabel}</p>
            </div>

            <div className="col-6">
              <label className="form-label fw-bold">الحالة الصحية</label>
              <p className="form-control">{details.health_status}</p>
            </div>

            <div className="col-6">
              <label className="form-label fw-bold">تاريخ العثور</label>
              <p className="form-control">{details.found_date}</p>
            </div>

            <div className="col-6">
              <label className="form-label fw-bold">موقع العثور</label>
              <p className="form-control">{details.found_location}</p>
            </div>

            <div className="col-12">
              <label className="form-label fw-bold">الجهة المسؤولة</label>
              <p className="form-control">{details.authority_name}</p>
            </div>

            <div className="col-6">
              <label className="form-label fw-bold">رقم التواصل 1</label>
              <p className="form-control">{details.phone_number1}</p>
            </div>

            <div className="col-6">
              <label className="form-label fw-bold">رقم التواصل 2</label>
              <p className="form-control">{details.phone_number2 || "—"}</p>
            </div>
          </div>
        </>
      )}
    </BaseModal>
  );
}
