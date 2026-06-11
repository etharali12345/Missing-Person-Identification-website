import { CardProfile } from "../../../components/shared/list/CardProfile";
import { useMyMissingReports } from "../hooks/useMyMissingReports";
import { UpdateMissingModal } from "../components/UpdateMissingModal";
import { DeleteMissingModal } from "../components/DeleteMissingModal";
import { MissingMatchModal } from "../components/MissingMatchModal";
import "../../../components/shared/list/CardsPage.css";

export function MyMissingReportsPage() {
  const {
    missingList,
    getMissingList,
    handleDelete,
    handleUpdate,
    updateError,
    clearUpdateError,
    handleMatchDetails,
    matchDetails,
    matchLoading,
    handleConfirmMatch,
    handleRejectMatch,
  } = useMyMissingReports();

  return (
    <div className="container pb-5">
      <h1 className="py-4 text-center topic">
        قائمة المفقودين الذين <span>اضفتهم</span>
      </h1>
      <div className="row g-1 pb-5 justify-content-center">
        <div className="row g-1 pb-5 justify-content-center">
          {missingList.length === 0 ? (
            <h3 className="text-center text-muted mt-1">
              لا يوجد مفقودين مضافين
            </h3>
          ) : (
            missingList.map((profile) => (
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
                  MatchDetailsModal={MissingMatchModal}
                  onMatchDetails={handleMatchDetails}
                  matchDetails={matchDetails}
                  matchLoading={matchLoading}
                  allowUncertainHandle={true}
                  onConfirmMatch={handleConfirmMatch}
                  onRejectMatch={handleRejectMatch}
                />
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
