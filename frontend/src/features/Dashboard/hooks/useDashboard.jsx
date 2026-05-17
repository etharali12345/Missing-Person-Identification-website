import { useState, useCallback, useEffect } from "react";
import {
  getAuthoritiesSVC,
  getAuthorityByIdSVC,
} from "../services/AuthorityRegisterService";

export function useDashboard() {
  const [authorities, setAuthorities] = useState([]);

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
    getAuthorities();
  }, [getAuthorities]);

  return { authorities, getAuthorities, getAuthorityById };
}
