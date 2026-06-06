import "./statCards.css";
import { ChartLine } from "lucide-react";

export function StatCards({ pendingCount, missingCount, foundCount }) {
  return (
    <div className="stat-cards-wrapper container py-4 px-4">
      <div className="row g-4 justify-content-center">
        <div className="col-12 col-md-4">
          <div className="stat-card stat-card-pending">
            <span className="stat-title stat-title-pending">
              عدد الطلبات قيد المراجعة
            </span>
            <span className="stat-value stat-value-pending">
              {pendingCount}
            </span>
          </div>
        </div>

        <div className="col-12 col-md-4">
          <div className="stat-card stat-card-gradient">
            <span className="stat-title stat-title-gradient">
              عدد بلاغات المفقودين هذا الشهر
            </span>
            <div className="stat-value-container">
              <ChartLine color="white" size={35} />
              <span className="stat-value stat-value-gradient">
                {missingCount}
              </span>
            </div>
          </div>
        </div>

        <div className="col-12 col-md-4">
          <div className="stat-card stat-card-gradient">
            <span className="stat-title stat-title-gradient">
              عدد بلاغات العثور هذا الشهر
            </span>
            <div className="stat-value-container">
              <ChartLine color="white" size={35} />
              <span className="stat-value stat-value-gradient">
                {foundCount}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
