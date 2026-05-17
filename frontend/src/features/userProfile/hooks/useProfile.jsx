import { useState, useEffect, useCallback } from "react";
import { getUserProfile, updateUserProfile } from "../services/ProfileService";

export const useProfile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getUserProfile();
        setProfile(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const handleProfile = useCallback(async (updatedData) => {
    try {
      setUpdating(true);
      setError(null);
      setSuccessMessage(null);
      await updateUserProfile(updatedData);
      setProfile((prev) => ({ ...prev, ...updatedData }));
      setSuccessMessage("تم تحديث الملف الشخصي بنجاح");
    } catch (err) {
      setError(err.message);
    } finally {
      setUpdating(false);
    }
  }, []);

  const resetState = useCallback(() => {
    setError(null);
    setSuccessMessage(null);
  }, []);

  return {
    profile,
    loading,
    updating,
    error,
    successMessage,
    handleProfile,
    resetState,
  };
};
