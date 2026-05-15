import { useState, useCallback, useEffect } from "react";
import { getAuthoritiesSVC } from "../services/DashboardServices";

export function useDashboard() {
  const [authorities, setAuthorities] = useState(null);

  const getAuthorities = useCallback(async (formData) => {
    try {
      const response = await getAuthoritiesSVC();
      setAuthorities(response);
    } catch (err) {
      console.error(err);
    }
  }, []);

  useEffect(() => {
    getAuthorities();
  }, [getAuthorities]);

  return { authorities };
}
