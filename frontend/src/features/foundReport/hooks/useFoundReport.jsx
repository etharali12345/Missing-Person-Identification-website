import { useState, useCallback } from "react";
import {
  submitFoundReportSVC,
  validateUncertainSVC,
} from "../services/FoundReportService";

export const useFoundReport = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [result, setResult] = useState(null);

  const submitReport = useCallback(async (formData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await submitFoundReportSVC(formData);
      setResult(response);
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const validateUncertain = useCallback(
    async (matchId, percentage, decision) => {
      try {
        await validateUncertainSVC(matchId, percentage, decision);
        if (decision === "confirmed") {
          setResult((prev) => ({ ...prev, status: "match" }));
        } else {
          setResult({ status: "no_match" });
        }
      } catch (error) {
        console.error(error);
      }
    },
    [],
  );

  return {
    submitReport,
    validateUncertain,
    loading,
    error,
    result,
  };
};
