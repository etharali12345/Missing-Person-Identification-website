import { MissingMatchResult } from "./MissingMatchResult";
import { MissingNoMatchResult } from "./MissingNoMatchResult";

export function MissingReportResult({ result, setShowForm }) {
  if (result.status === "no_match") {
    setShowForm(false);
    return <MissingNoMatchResult />;
  }
  if (result.status === "match" || result.status === "uncertain") {
    return <MissingMatchResult result={result} />;
  }
}
