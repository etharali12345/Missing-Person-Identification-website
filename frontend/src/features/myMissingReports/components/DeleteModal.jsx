import { BaseModal } from "../../../components/shared/list/BaseModal";

export function DeleteModal({ show, onConfirm, onCancel }) {
  return (
    <BaseModal
      show={show}
      title="تأكيد الحذف"
      onCancel={onCancel}
      direction="reverse"
      footer={
        <>
          <button className="btn btn-danger" onClick={onConfirm}>
            نعم، احذف
          </button>
          <button className="btn btn-secondary" onClick={onCancel}>
            إلغاء
          </button>
        </>
      }
    >
      <p>
        هل أنت متأكد أنك تريد حذف هذا البلاغ؟ لا يمكن التراجع عن هذا الإجراء.
      </p>
    </BaseModal>
  );
}
