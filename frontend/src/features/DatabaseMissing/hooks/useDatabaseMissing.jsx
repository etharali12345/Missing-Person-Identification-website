import { useState, useCallback, useEffect } from "react";
import {
  getMissingDB,
  getMissingById,
  deleteMissing,
  getMatchDetails,
  cancelMatch,
} from "../services/DatabaseMissing.Service";

export function useDatabaseMissing() {
  const [foundList, setFoundList] = useState([]);
  const [updateError, setUpdateError] = useState(null);
  const [matchDetails, setMatchDetails] = useState(null);
  const [matchLoading, setMatchLoading] = useState(false);

  const getMissingDBList = useCallback(async () => {
    try {
      const response = await getMissingDB();
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
  };
}
