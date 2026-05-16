import { useState, useCallback, useEffect } from "react";
import {
  getMissingDB,
  getMissingById,
  deleteMissing,
  getMatchDetails,
  cancelMatch,
} from "../services/DatabaseMissing.Service";

export function useDatabaseMissing() {
  const [missingList, setMissingList] = useState([]);
  const [missing, setMissing] = useState(null);
  const [missingLoading, setMissingLoading] = useState(false);
  const [matchDetails, setMatchDetails] = useState(null);
  const [matchLoading, setMatchLoading] = useState(false);

  const getMissingDBList = useCallback(async () => {
    try {
      const response = await getMissingDB();
      setMissingList(response);
    } catch (err) {
      console.error(err);
    }
  }, []);

  const handleMissing = useCallback(async (id) => {
    try {
      setMissing(null);
      setMissingLoading(true);
      const data = await getMissingById(id);
      setMissing(data);
    } catch (err) {
      console.error(err);
    } finally {
      setMissingLoading(false);
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
      setMissingList((prev) =>
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
    getMissingDBList();
  }, [getMissingDBList]);

  return {
    missingList,
    getMissingDBList,
    missing,
    missingLoading,
    handleMissing,
    handleDelete,
    matchDetails,
    matchLoading,
    handleMatchDetails,
    handleCancelMatch,
  };
}
