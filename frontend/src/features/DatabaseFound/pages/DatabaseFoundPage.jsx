import { useState } from "react";
import { CardProfile } from "../../../components/shared/list/CardProfile";
import { useDatabaseFound } from "../hooks/useDatabaseFound";
import { DeleteFoundModal } from "../../myFoundReports/components/DeleteFoundModal";
import { FoundMatchModal } from "../../myFoundReports/components/FoundMatchModal";
import { ViewFoundCaseModal } from "../components/ViewFoundCaseModal";
import "../../../components/shared/list/CardsPage.css";
import { FilterDB } from "../../DatabaseMissing/components/FilterDB";

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

  const [nameInput, setNameInput] = useState("");
  const [statusInput, setStatusInput] = useState("");
  const [activeFilters, setActiveFilters] = useState({ name: "", status: "" });

  const handleFilter = () => {
    setActiveFilters({ name: nameInput.trim(), status: statusInput });
  };

  const filteredList = foundList.filter((profile) => {
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
        قاعدة بيانات <span>المعثورين عليهم</span>
      </h1>

      <FilterDB
        nameInput={nameInput}
        setNameInput={setNameInput}
        statusInput={statusInput}
        setStatusInput={setStatusInput}
        handleFilter={handleFilter}
        isMissing={false}
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
          ))
        )}
      </div>
    </div>
  );
}
