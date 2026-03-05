import { useState, useCallback } from "react";
import { submitMissingReportSVC } from "../services/MissingReportService";

export const useMissingReport = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [result, setResult] = useState({
    status: "match",
    mathcId: "54545435",
    percentage: 0.81,
    details: {
      name: "احمد محمد احمد ",
      approximate_age: 34,
      gender: "male",
      foun_date: "2026/4/4",
      found_location: "الشمالية- واد ي سيدنا",
      image: "/images/found_123.jpg",
      authority_name: "منظمة الهلال الاحمر",
      phone_number1: "0249943675432",
      phone_number2: "0249945646465",
    },
  });

  const submitReport = useCallback(async (formData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await submitMissingReportSVC(formData);
      setResult(response);
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
