import { CardProfile } from "../../../components/shared/list/CardProfile";
import { useMyMissingReports } from "../hooks/useMyMissingReports";
import "../../../components/shared/list/CardsPage.css";

export function MyMissingReportsPage() {
  const { missingList, getMissingList, handleDelete, handleUpdate } =
    useMyMissingReports();

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
              onDelete={handleDelete}
              onUpdate={handleUpdate}
              onDetails={() => {}}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
