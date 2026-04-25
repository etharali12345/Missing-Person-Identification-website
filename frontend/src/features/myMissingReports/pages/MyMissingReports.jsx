import { CardProfile } from "../../../components/shared/list/CardProfile";
import { useMyMissingReports } from "../hooks/useMyMissingReports";
import { UpdateMissingModal } from "../components/UpdateMissingModal";
import { DeleteMissingModal } from "../components/DeleteMissingModal";
import "../../../components/shared/list/CardsPage.css";

export function MyMissingReportsPage() {
  const {
    missingList,
    getMissingList,
    handleDelete,
    handleUpdate,
    updateError,
    clearUpdateError,
  } = useMyMissingReports();

  return (
    <div className="container pb-5">
      <h1 className="py-4 text-center topic">
        قائمة المفقودين الذين <span>اضفتهم</span>
      </h1>
      <div className="row g-1 pb-5 justify-content-center">
        {missingList.map((profile) => (
          <div
            key={profile.id}
            className="col-12 col-sm-6 col-lg-4 col-xl-3 d-flex justify-content-center"
          >
            <CardProfile
              profile={profile}
              DeleteModal={DeleteMissingModal}
              onDelete={handleDelete}
              UpdateModal={UpdateMissingModal}
              onUpdate={handleUpdate}
              updateError={updateError}
              clearUpdateError={clearUpdateError}
              onDetails={() => {}}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
