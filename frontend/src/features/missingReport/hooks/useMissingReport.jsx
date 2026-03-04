import { useState, useCallback } from "react";
import { submitMissingReportSVC } from "../services/MissingReportService";

export const useMissingReport = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [result, setResult] = useState(null);

  const submitReport = useCallback(async (formData) => {
    try {
      console.log("entered hook");
      setLoading(true);
      setError(null);

      const res = await submitMissingReportSVC(formData);
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const validateMatch = async (matchId, decision) => {
    try {
      /*await validateMissingMatch(matchId, decision);

      setResult((prev) => ({
        ...prev,
        status: decision === "confirmed" ? "match" : "no_match",
      }));
      */
    } catch (error) {
      console.error(error);
    }
  };

  return {
    submitReport,
    validateMatch,
    loading,
    error,
    result,
  };
};
