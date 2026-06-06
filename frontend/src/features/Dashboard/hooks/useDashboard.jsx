import { useState, useCallback, useEffect } from "react";
import {
  getAuthoritiesSVC,
  getAuthorityByIdSVC,
  getDashboardStatsSVC,
} from "../services/AuthorityRegisterService";

export function useDashboard() {
  const [authorities, setAuthorities] = useState([]);
  const [stats, setStats] = useState({
    pendingCount: 0,
    missingCount: 0,
    foundCount: 0,
  });

  const getAuthorities = useCallback(async () => {
    try {
      const response = await getAuthoritiesSVC();
      setAuthorities(response);
    } catch (err) {
      console.error(err);
    }
  }, []);

  const getAuthorityById = useCallback(async (authorityId) => {
    try {
      const response = await getAuthorityByIdSVC(authorityId);
      return response;
    } catch (err) {
      console.error(err);
      throw err;
    }
  }, []);

  useEffect(() => {
    const loadDashboard = async () => {
      const [authResult, statsResult] = await Promise.allSettled([
        getAuthoritiesSVC(),
        getDashboardStatsSVC(),
      ]);

      if (authResult.status === "fulfilled") setAuthorities(authResult.value);
      if (statsResult.status === "fulfilled") {
        const { pending_count, missing_this_month, found_this_month } =
          statsResult.value;
        setStats({
          pendingCount: pending_count,
          missingCount: missing_this_month,
          foundCount: found_this_month,
        });
      }
    };

    loadDashboard();
  }, []);

  return { authorities, getAuthorities, getAuthorityById, stats };
}
