import axios from "axios";

//export const BASE_URL = "http://127.0.0.1:5000";
export const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

export const api = axios.create({
  baseURL: `${BASE_URL}/api`,
  withCredentials: true,
});
