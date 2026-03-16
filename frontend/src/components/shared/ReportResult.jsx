import { useEffect } from "react";
import { MatchResult } from "./MatchResult";
import { NoMatchResult } from "./NoMatchResult";
import "./ReportResult.css";

export function ReportResult({
  result,
  setShowForm,
  noMatchMessage,
  DetailsComponent,
  validateUncertain,
}) {
  useEffect(() => {
    if (result.status === "no_match") setShowForm(false);
  }, [result.status]);

  if (result.status === "no_match") {
    return <NoMatchResult message={noMatchMessage} />;
  }
  if (result.status === "match" || result.status === "uncertain") {
    return (
      <MatchResult
        result={result}
        DetailsComponent={DetailsComponent}
        validateUncertain={validateUncertain}
      />
    );
  }
}
