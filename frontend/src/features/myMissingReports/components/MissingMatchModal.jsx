import { BaseModal } from "../../../components/shared/list/BaseModal";
import { ImageShow } from "../../../components/shared/ImageShow";
import { CircularProgress } from "../../../components/shared/CircularProgress";
import { LinearProgress } from "../../../components/shared/LinearProgress";
import { MissingMatchDetails } from "../../missingReport/components/result/MissingMatchDetails";
import { useState, useRef, useEffect } from "react";
import "../../../components/shared/ReportResult.css";

export function MissingMatchModal({
  show,
  details,
  loading,
  onCancel,
  onCancelMatch,
  matchId,
  status = "match",
  allowUncertainHandle = false,
  onConfirmMatch,
  onRejectMatch,
}) {
  const [showMatchCancelConfirm, setMatchCancelConfirm] = useState(false);

  const isUncertain = status === "uncertain";
  const isMatch = status === "match";

  const genderLabel = details?.gender === "male" ? "ذكر" : "أنثى";
  const percentage = details?.percentage
    ? `${Math.round(details.percentage * 100)}%`
    : null;

  const confirmRef = useRef(null);

  const handleCancel = () => {
    setMatchCancelConfirm(false);
    onCancel();
  };

  const handleCancelMatchClick = () => setMatchCancelConfirm(true);

  const handleConfirmYes = () => {
    setMatchCancelConfirm(false);
    onCancelMatch(matchId);
    onCancel();
  };

  const handleConfirmNo = () => setMatchCancelConfirm(false);

  const handleConfirmMatch = () => {
    onConfirmMatch(matchId);
    onCancel();
  };

  const handleRejectMatch = () => {
    onRejectMatch(matchId);
    onCancel();
  };

  useEffect(() => {
    if (showMatchCancelConfirm && confirmRef.current) {
      const modalBody = confirmRef.current.closest(".modal-body");
      if (modalBody) modalBody.scrollTop = modalBody.scrollHeight;
    }
  }, [showMatchCancelConfirm]);

  // Derive which action section to show
  const showCancelMatch = isMatch && onCancelMatch;
  const showUncertainActions = isUncertain && allowUncertainHandle;

  return (
    <BaseModal
      show={show}
      title="تفاصيل التطابق"
      onCancel={handleCancel}
      customClass="custome-modal"
      footer={
        <button type="button" className="btn-close" onClick={handleCancel} />
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
            <p
              className="percentage"
              style={{ color: isUncertain ? "#ce9c07" : "green" }}
            >
              {percentage}
            </p>

            <LinearProgress
              value={details.percentage}
              color={isUncertain ? "yellow" : "green"}
            />
            <MissingMatchDetails details={details} />

            {/* Uncertain: confirm or reject */}
            {showUncertainActions && (
              <>
                <p className="text-center t fw-bold mb-3 mt-2">
                  هل هذا هو نفس الشخص؟
                </p>

                <div className="d-flex gap-2">
                  <button
                    className="btn btn-ok w-50"
                    onClick={handleConfirmMatch}
                  >
                    نعم، نفس الشخص
                  </button>

                  <button
                    className="btn btn-no w-50"
                    onClick={handleRejectMatch}
                  >
                    لا، ليس نفس الشخص
                  </button>
                </div>
              </>
            )}

            {/* Match: cancel (not shown for uncertain) */}
            {showCancelMatch && (
              <button
                className="btn btn-cancle-match w-100 mt-3"
                onClick={handleCancelMatchClick}
              >
                إلغاء التطابق
              </button>
            )}

            {showMatchCancelConfirm && (
              <div ref={confirmRef} className="mt-3 text-center">
                <p>هل أنت متأكد من إلغاء التطابق؟</p>
                <div className="d-flex gap-2 justify-content-center">
                  <button
                    className="btn btn-danger w-25"
                    onClick={handleConfirmYes}
                  >
                    نعم
                  </button>
                  <button
                    className="btn btn-secondary w-25"
                    onClick={handleConfirmNo}
                  >
                    لا
                  </button>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </BaseModal>
  );
}
