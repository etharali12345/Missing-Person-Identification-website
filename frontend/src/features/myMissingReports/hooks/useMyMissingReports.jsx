import { useState, useCallback, useEffect } from "react";
import {
  getMissings,
  deleteMissing,
  updateMissing,
  getMatchDetails,
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
  };
}
