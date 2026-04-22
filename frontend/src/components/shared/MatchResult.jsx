import { ImageShow } from "./ImageShow";
import { CircularProgress } from "./CircularProgress";
import { LinearProgress } from "./LinearProgress";
import { ConfirmButtons } from "./ConfirmButtons";

export function MatchResult({
  result,
  DetailsComponent,
  validateUncertain = null,
}) {
  const isUncertain = result.status === "uncertain";
  const color = isUncertain ? "yellow" : "green";

  return (
    <div className="center-flex flex-column w-100">
      <ImageShow image={result.details.image_path} />
      <div className="glass-reportCard">
        <div className="circular-contaier">
          <CircularProgress value={result.percentage} color={color} />
        </div>
        <div className="mt-4">
          <h6>{`الحالة: ${isUncertain ? "غير مؤكدة" : "تطابق"}`}</h6>
          {isUncertain && (
            <h6 className="small">
              نرجو التحقق من البيانات،وتأكيد ما إذا كان نفس الشخص أم لا
            </h6>
          )}
        </div>
        <LinearProgress value={result.percentage} color={color} />
        <DetailsComponent details={result.details} />
        {isUncertain && (
          <ConfirmButtons
            matchId={result.matchId}
            percentage={result.percentage}
            onDecision={validateUncertain}
          />
        )}
      </div>
    </div>
  );
}
