import { ImageShow } from "../../../components/shared/ImageShow";
import { CircularProgress } from "../../../components/shared/CircularProgress";
import { LinearProgress } from "../../../components/shared/LinearProgress";
import { MissingResultFields } from "./MissingResultFields";
import { ConfirmButtons } from "../../../components/shared/ConfirmButtons";

export function MissingMatchResult({ result, validateMatch }) {
  const isUncertain = result.status === "uncertain";
  const color = isUncertain ? "yellow" : "green";
  return (
    <div className="center-flex flex-column w-100">
      <ImageShow image={result.details.image} />
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
        <MissingResultFields details={result.details} />
        {isUncertain ? (
          <ConfirmButtons matchId={result.matchId} onDecision={validateMatch} />
        ) : (
          ""
        )}
      </div>
    </div>
  );
}
