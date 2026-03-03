import { useState } from "react";

export const useMissingReport = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const submitReport = async (formData) => {
    return <></>;
  };

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
    result,
  };
};
