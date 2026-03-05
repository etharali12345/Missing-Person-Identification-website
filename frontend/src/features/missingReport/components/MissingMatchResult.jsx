import { ImageShow } from "../../../components/shared/ImageShow";
import { CircularProgress } from "../../../components/shared/CircularProgress";

export function MissingMatchResult({ result }) {
  return (
    <div className="center-flex flex-column w-100">
      <ImageShow image={result.details.image} />
      <div className="glass-reportCard">
        <div className="circular-contaier">
          <CircularProgress />
        </div>
      </div>
    </div>
  );
}
