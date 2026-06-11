import { CardProfile } from "../../../components/shared/list/CardProfile";
import { useMyFoundReports } from "../hooks/useMyFoundReports";
import { UpdateFoundModal } from "../components/UpdateFoundModal";
import { DeleteFoundModal } from "../components/DeleteFoundModal";
import { FoundMatchModal } from "../components/FoundMatchModal";
import "../../../components/shared/list/CardsPage.css";

export function MyFoundReportsPage() {
  const {
    foundList,
    getFoundList,
    handleDelete,
    handleUpdate,
    updateError,
    clearUpdateError,
    handleMatchDetails,
    matchDetails,
    matchLoading,
    handleCancelMatch,
    handleConfirmMatch,
    handleRejectMatch,
  } = useMyFoundReports();

  return (
    <div className="container pb-5">
      <h1 className="py-4 text-center topic">
        قائمة المعثورين الذين <span>اضفتهم</span>
      </h1>
      <div className="row g-1 pb-5 justify-content-center">
        {foundList.length === 0 ? (
          <h3 className="text-center text-muted mt-1">
            لا يوجد معثورين مضافين
          </h3>
        ) : (
          foundList.map((profile) => (
            <div
              key={profile.id}
              className="col-12 col-sm-6 col-lg-4 col-xl-3 d-flex justify-content-center"
            >
              <CardProfile
                profile={profile}
                DeleteModal={DeleteFoundModal}
                onDelete={handleDelete}
                UpdateModal={UpdateFoundModal}
                onUpdate={handleUpdate}
                updateError={updateError}
                clearUpdateError={clearUpdateError}
                MatchDetailsModal={FoundMatchModal}
                onMatchDetails={handleMatchDetails}
                matchDetails={matchDetails}
                matchLoading={matchLoading}
                onCancelMatch={handleCancelMatch}
                allowUncertainHandle={true}
                onConfirmMatch={handleConfirmMatch}
                onRejectMatch={handleRejectMatch}
              />
            </div>
          ))
        )}
      </div>
    </div>
  );
}
