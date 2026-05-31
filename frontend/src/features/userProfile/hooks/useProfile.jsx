import { useState, useEffect, useCallback } from "react";
import {
  getUserProfile,
  updateUserInfo,
  updateUserPassword,
} from "../services/ProfileService";

export function useProfile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [updatingPassword, setUpdatingPassword] = useState(false);
  const [error, setError] = useState(null);
  const [passwordError, setPasswordError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [passwordSuccessMessage, setPasswordSuccessMessage] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
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

  const handleProfile = useCallback(async (infoData) => {
    setUpdating(true);
    setError(null);
    setSuccessMessage(null);

    try {
      await updateUserInfo(infoData);
      setProfile((prev) => ({
        ...prev,
        first_name: infoData.first_name,
        last_name: infoData.last_name,
        email_or_phone: infoData.email_or_phone,
      }));
      setSuccessMessage("تم تحديث البيانات بنجاح");
    } catch (err) {
      setError(err.message);
    } finally {
      setUpdating(false);
    }
  }, []);

  const handlePassword = useCallback(async (passwordData) => {
    setUpdatingPassword(true);
    setPasswordError(null);
    setPasswordSuccessMessage(null);

    try {
      await updateUserPassword(passwordData);
      setPasswordSuccessMessage("تم تحديث  البيانات وكلمة المرور بنجاح");
    } catch (err) {
      setPasswordError(err.message);
    } finally {
      setUpdatingPassword(false);
    }
  }, []);

  const resetState = useCallback(() => {
    setError(null);
    setPasswordError(null);
    setSuccessMessage(null);
    setPasswordSuccessMessage(null);
  }, []);

  return {
    profile,
    loading,
    updating,
    updatingPassword,
    error,
    passwordError,
    successMessage,
    passwordSuccessMessage,
    handleProfile,
    handlePassword,
    resetState,
  };
}
