import axios from "axios";
import { Phone } from "lucide-react";

const BASE_URL = "http://localhost:5000";

const api = axios.create({
  baseURL: `${BASE_URL}/api`,
  withCredentials: true,
});

export const getMissingDB = async () => {
  try {
    const res = await api.get("/missing-database");
    const data = res.data;
    return data.map((item) => ({
      ...item,
      image_path: item.image_path ? `${BASE_URL}/${item.image_path}` : null,
    }));
  } catch (error) {
    throw new Error("Getting the Missing Database Entries Failed");
  }
};

export const getMissingById = async (id) => {
  try {
    const res = await api.get(`/missing-database/${id}`);
    const data = res.data;
    return {
      ...data,
      image_path: data.image_path ? `${BASE_URL}/${data.image_path}` : null,
    };
  } catch (error) {
    throw new Error("Getting the Missing Database Entries Failed");
  }
};

export const deleteMissing = async (id) => {
  try {
    await api.delete(`/missing-database/${id}`);
  } catch (error) {
    throw new Error("Deleting the Missing Database Entry Failed");
  }
};

export const getMatchDetails = async (matchId) => {
  try {
    const res = await api.get(`/missing-database-match/${matchId}`);
    const data = res.data;
    if (data?.image_path) {
      data.image_path = `${BASE_URL}/${data.image_path}`;
    }
    return data;
  } catch (error) {
    throw new Error("Getting Match of Missing Failed");
  }
};

export const cancelMatch = async (matchId) => {
  try {
    await api.patch(`/missing-database-match/${matchId}/cancel`);
  } catch (error) {
    throw new Error("Cancel Match of Missing Failed");
  }
};
