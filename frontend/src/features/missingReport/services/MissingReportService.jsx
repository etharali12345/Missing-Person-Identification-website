import axios from "axios";

const BASE_URL = "http://localhost:5000";

const api = axios.create({
  baseURL: `${BASE_URL}/api`,
  withCredentials: true,
});

export const submitMissingReportSVC = async (formData) => {
  console.log([...formData.entries()]);
  return null;
  try {
    const res = await api.post("/missing-report/send", formData);
    const data = res.data;
    if (data.details?.image) {
      data.details.image = `${BASE_URL}${data.details.image}`;
    }
    return data;
  } catch (error) {
    throw new Error(
      error.response?.data?.message || "فشل الارسال الرجاء المحاولة مرةأخرى",
    );
  }
};

export const validateMissingMatch = async (matchId, decision) => {
  try {
    const response = await api.post(`/missing-report/${matchId}/validate`, {
      decision,
    });

    return response.data;
  } catch (error) {
    throw error.response?.data || { message: "Validation failed" };
  }
};
