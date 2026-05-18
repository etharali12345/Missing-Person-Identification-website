import { useState } from "react";
import { CardProfile } from "../../../components/shared/list/CardProfile";
import { useDatabaseMissing } from "../hooks/useDatabaseMissing";
import { DeleteMissingModal } from "../../myMissingReports/components/DeleteMissingModal";
import { MissingMatchModal } from "../../myMissingReports/components/MissingMatchModal";
import { ViewMissingCaseModal } from "../components/ViewMissingCaseModal";
import "../../../components/shared/list/CardsPage.css";
import { useAuth } from "../../../context/AuthContext";
import { FilterDB } from "../components/FilterDB";

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

  const { user } = useAuth();
  const isAdmin = user.role === "admin";

  const [nameInput, setNameInput] = useState("");
  const [statusInput, setStatusInput] = useState("");
  const [activeFilters, setActiveFilters] = useState({ name: "", status: "" });

  const handleFilter = () => {
    setActiveFilters({ name: nameInput.trim(), status: statusInput });
  };

  const filteredList = missingList.filter((profile) => {
    const matchesName = activeFilters.name
      ? profile.full_name.includes(activeFilters.name)
      : true;
    const matchesStatus = activeFilters.status
      ? profile.status === activeFilters.status
      : true;
    return matchesName && matchesStatus;
  });

  return (
    <div className="container pb-5">
      <h1 className="py-4 text-center topic">
        قاعدة بيانات <span>المفقودين</span>
      </h1>

      <FilterDB
        nameInput={nameInput}
        setNameInput={setNameInput}
        statusInput={statusInput}
        setStatusInput={setStatusInput}
        handleFilter={handleFilter}
      />

      <div className="row g-1 pb-5 justify-content-center">
        {filteredList.length === 0 ? (
          <h4 className="text-center w-100 text-secondary m-5 p-5">
            لا توجد نتائج
          </h4>
        ) : (
          filteredList.map((profile) => (
            <div
              key={profile.id}
              className="col-12 col-sm-6 col-lg-4 col-xl-3 d-flex justify-content-center"
            >
              <CardProfile
                profile={profile}
                DeleteModal={isAdmin ? DeleteMissingModal : undefined}
                onDelete={handleDelete}
                MatchDetailsModal={MissingMatchModal}
                onMatchDetails={handleMatchDetails}
                matchDetails={matchDetails}
                matchLoading={matchLoading}
                onCancelMatch={isAdmin ? handleCancelMatch : undefined}
                ViewCaseProfileModal={ViewMissingCaseModal}
                onCaseProfile={handleGetMissingById}
                caseProfile={missing}
                caseProfileLoading={missingLoading}
              />
            </div>
          ))
        )}
      </div>
    </div>
  );
}
