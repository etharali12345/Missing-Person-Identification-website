import { useState, useCallback, useEffect } from "react";
import {
  getFounds,
  deleteFound,
  updateFound,
  getMatchDetails,
  cancelMatch,
  confirmUncertainMatch,
  rejectUncertainMatch,
} from "../services/MyFoundServices";

export function useMyFoundReports() {
  const [foundList, setFoundList] = useState([]);
  const [updateError, setUpdateError] = useState(null);
  const [matchDetails, setMatchDetails] = useState(null);
  const [matchLoading, setMatchLoading] = useState(false);

  const getFoundList = useCallback(async () => {
    try {
      const response = await getFounds();
      setFoundList(response);
    } catch (err) {
      console.error(err);
    }
  }, []);

  const handleDelete = useCallback(async (id) => {
    try {
      await deleteFound(id);
      setFoundList((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      console.error(err);
    }
  }, []);

  const handleUpdate = useCallback(async (id, updatedData) => {
    try {
      setUpdateError(null);
      await updateFound(id, updatedData);
      setFoundList((prev) =>
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

  const handleCancelMatch = useCallback(async (matchId) => {
    try {
      await cancelMatch(matchId);
      setFoundList((prev) =>
        prev.map((item) =>
          item.matchId === matchId
            ? { ...item, status: "no_match", matchId: undefined }
            : item,
        ),
      );
    } catch (err) {
      console.error(err);
    }
  }, []);

  const handleConfirmMatch = useCallback(async (matchId) => {
    try {
      await confirmUncertainMatch(matchId);
      setFoundList((prev) =>
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
      setFoundList((prev) =>
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
    getFoundList();
  }, [getFoundList]);

  return {
    foundList,
    getFoundList,
    handleDelete,
    handleUpdate,
    updateError,
    clearUpdateError,
    handleMatchDetails,
    matchDetails,
    matchLoading,
    handleCancelMatch,
    handleConfirmMatch,
    handleRejectMatch,
  };
}
