import { useState } from "react";
import { CardImage } from "./CardImage";
import { SquarePen, Trash2 } from "lucide-react";

export function CardProfile({
  profile,
  DeleteModal,
  onDelete,
  UpdateModal,
  onUpdate,
  updateError,
  clearUpdateError,
}) {
  const isMatch = profile.status === "match";
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showUpdateModal, setShowUpdateModal] = useState(false);

  const handleDeleteConfirm = () => {
    onDelete(profile.id);
    setShowDeleteModal(false);
  };

  const handleUpdateConfirm = async (id, updatedData) => {
    const success = await onUpdate(id, updatedData);
    if (success) setShowUpdateModal(false);
  };

  return (
    <>
      <div className="profile-card text-center">
        <CardImage
          src={profile.image_path}
          alt={profile.full_name}
          status={profile.status}
        />

        <div className="profile-text">
          <div className="profile-name">{profile.full_name}</div>
          <div className="profile-status-label">
            الحالة: {isMatch ? "تطابق" : "لا تطابق"}
          </div>
        </div>

        {isMatch ? (
          <>
            <div className="btn-edit-contaier">
              <button
                className="btn-edit"
                onClick={() => setShowUpdateModal(true)}
              >
                تعديل
                <SquarePen size={18} />
              </button>
            </div>
            <div className="action-row">
              <button
                className="btn-delete"
                onClick={() => setShowDeleteModal(true)}
              >
                حذف البلاغ
                <Trash2 size={18} />
              </button>
              <button className="btn-details">تفاصيل التطابق</button>
            </div>
          </>
        ) : (
          <div className="action-row">
            <button
              className="btn-delete"
              onClick={() => setShowDeleteModal(true)}
            >
              حذف البلاغ
              <Trash2 size={18} />
            </button>
            <button
              className="btn-edit"
              onClick={() => setShowUpdateModal(true)}
            >
              تعديل
              <SquarePen size={18} />
            </button>
          </div>
        )}
      </div>

      <DeleteModal
        show={showDeleteModal}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setShowDeleteModal(false)}
      />

      <UpdateModal
        show={showUpdateModal}
        profile={profile}
        onConfirm={handleUpdateConfirm}
        onCancel={() => {
          clearUpdateError();
          setShowUpdateModal(false);
        }}
        updateError={updateError}
      />
    </>
  );
}
