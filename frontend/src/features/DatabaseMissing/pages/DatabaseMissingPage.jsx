import { CardProfile } from "../../../components/shared/list/CardProfile";
import { useDatabaseMissing } from "../hooks/useDatabaseMissing";

import { DeleteMissingModal } from "../../myMissingReports/components/DeleteMissingModal";
import { MissingMatchModal } from "../../myMissingReports/components/MissingMatchModal";
import { ViewMissingCaseModal } from "../components/ViewMissingCaseModal";
import "../../../components/shared/list/CardsPage.css";

export function DatabaseMissingPage() {
  const {
    missingList,
    handleGetMissingById,
    missingLoading,
    missing,
    handleDelete,
    handleMatchDetails,
    matchDetails,
    matchLoading,
    handleCancelMatch,
  } = useDatabaseMissing();

  return (
    <div className="container pb-5">
      <h1 className="py-4 text-center topic">
        قاعدة بيانات <span>المفقودين</span>
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
              MatchDetailsModal={MissingMatchModal}
              onMatchDetails={handleMatchDetails}
              matchDetails={matchDetails}
              matchLoading={matchLoading}
              onCancelMatch={handleCancelMatch}
              ViewCaseProfileModal={ViewMissingCaseModal}
              onCaseProfile={handleGetMissingById}
              caseProfile={missing}
              caseProfileLoading={missingLoading}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
