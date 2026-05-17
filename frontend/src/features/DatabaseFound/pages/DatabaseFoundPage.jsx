import { CardProfile } from "../../../components/shared/list/CardProfile";
import { useDatabaseFound } from "../hooks/useDatabaseFound";
import { DeleteFoundModal } from "../../myFoundReports/components/DeleteFoundModal";
import { FoundMatchModal } from "../../myFoundReports/components/FoundMatchModal";
import { ViewFoundCaseModal } from "../components/ViewFoundCaseModal";
import "../../../components/shared/list/CardsPage.css";

export function DatabaseFoundPage() {
  const {
    foundList,
    handleGetFoundById,
    foundLoading,
    found,
    handleDelete,
    handleMatchDetails,
    matchDetails,
    matchLoading,
    handleCancelMatch,
  } = useDatabaseFound();

  return (
    <div className="container pb-5">
      <h1 className="py-4 text-center topic">
        قاعدة بيانات <span>المعثورين عليهم</span>
      </h1>
      <div className="row g-1 pb-5 justify-content-center">
        {foundList.map((profile) => (
          <div
            key={profile.id}
            className="col-12 col-sm-6 col-lg-4 col-xl-3 d-flex justify-content-center"
          >
            <CardProfile
              profile={profile}
              DeleteModal={DeleteFoundModal}
              onDelete={handleDelete}
              MatchDetailsModal={FoundMatchModal}
              onMatchDetails={handleMatchDetails}
              matchDetails={matchDetails}
              matchLoading={matchLoading}
              onCancelMatch={handleCancelMatch}
              ViewCaseProfileModal={ViewFoundCaseModal}
              onCaseProfile={handleGetFoundById}
              caseProfile={found}
              caseProfileLoading={foundLoading}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
