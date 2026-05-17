import { BaseModal } from "../../../components/shared/list/BaseModal";
import { FoundMatchDetails } from "../../foundReport/components/result/FoundMatchDetails";
import { CircleX } from "lucide-react";

export function ViewMissingCaseModal({ show, profile, loading, onCancel }) {
  return (
    <BaseModal
      show={show}
      title="تفاصيل المفقود"
      onCancel={onCancel}
      customClass="custome-modal"
      footer={
        <button type="button" className="btn-close" onClick={onCancel}></button>
      }
    >
      {loading && (
        <div className="text-center py-4">
          <div className="spinner-border text-primary" role="status" />
          <p className="mt-2">جاري التحميل...</p>
        </div>
      )}

      {!loading && profile && (
        <>
          <div className="d-flex justify-content-center custome-image">
            <img src={profile.image_path} alt={profile.full_name} />
          </div>
          <div className="px-3 py-4 custome-form">
            <h5 className="text-center">معلومات المفقود</h5>
            <FoundMatchDetails details={profile} />
          </div>
        </>
      )}
    </BaseModal>
  );
}
