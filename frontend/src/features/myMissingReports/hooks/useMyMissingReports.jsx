import { useState, useCallback, useEffect } from "react";
import {
  getMissings,
  deleteMissing,
  updateMissing,
} from "../services/MyMissingServices";

export function useMyMissingReports() {
  const [missingList, setMissingList] = useState([]);

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
      await updateMissing(id, updatedData);
      setMissingList((prev) =>
        prev.map((item) =>
          item.id === id ? { ...item, ...updatedData } : item,
        ),
      );
    } catch (err) {
      console.error(err);
    }
  }, []);

  useEffect(() => {
    getMissingList();
  }, [getMissingList]);

  return { missingList, getMissingList, handleDelete, handleUpdate };
}
