import { useState, useCallback, useEffect } from "react";
import {
  getMissings,
  deleteMissing,
  updateMissing,
  getMatchDetails,
  confirmUncertainMatch,
  rejectUncertainMatch,
} from "../services/MyMissingServices";

export function useMyMissingReports() {
  const [missingList, setMissingList] = useState([]);
  const [updateError, setUpdateError] = useState(null);
  const [matchDetails, setMatchDetails] = useState(null);
  const [matchLoading, setMatchLoading] = useState(false);

  const getMissingList = useCallback(async () => {
    try {
      const response = await getMissings();
      setMissingList(response);
    } catch (err) {
      console.error(err);
    }
  }, []);

  const handleDelete = useCallback(async (id) => {
    try {
      await deleteMissing(id);
      setMissingList((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      console.error(err);
    }
  }, []);

  const handleUpdate = useCallback(async (id, updatedData) => {
    try {
      setUpdateError(null);
      await updateMissing(id, updatedData);
      setMissingList((prev) =>
        prev.map((item) =>
          item.id === id ? { ...item, ...updatedData } : item,
        ),
      );
      return true;
    } catch (err) {
      setUpdateError(err.message);
      return false;
    }
  }, []);

  const clearUpdateError = useCallback(() => {
    setUpdateError(null);
  }, []);

  const handleMatchDetails = useCallback(async (matchId) => {
    try {
      setMatchDetails(null);
      setMatchLoading(true);
      const data = await getMatchDetails(matchId);
      setMatchDetails(data);
    } catch (err) {
      console.error(err);
    } finally {
      setMatchLoading(false);
    }
  }, []);

  const handleConfirmMatch = useCallback(async (matchId) => {
    try {
      await confirmUncertainMatch(matchId);
      setMissingList((prev) =>
        prev.map((item) =>
          item.matchId === matchId ? { ...item, status: "match" } : item,
        ),
      );
    } catch (err) {
      console.error(err);
    }
  }, []);

  const handleRejectMatch = useCallback(async (matchId) => {
    try {
      await rejectUncertainMatch(matchId);
      setMissingList((prev) =>
        prev.map((item) =>
          item.matchId === matchId
            ? { ...item, status: "nomatch", matchId: undefined }
            : item,
        ),
      );
    } catch (err) {
      console.error(err);
    }
  }, []);

  useEffect(() => {
    getMissingList();
  }, [getMissingList]);

  return {
    missingList,
    getMissingList,
    handleDelete,
    handleUpdate,
    updateError,
    clearUpdateError,
    handleMatchDetails,
    matchDetails,
    matchLoading,
    handleConfirmMatch,
    handleRejectMatch,
  };
}
