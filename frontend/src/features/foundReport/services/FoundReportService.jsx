import axios from "axios";

const BASE_URL = "http://127.0.0.1:5000";

const api = axios.create({
  baseURL: `${BASE_URL}/api`,
  withCredentials: true,
});

export const submitFoundReportSVC = async (formData) => {
  try {
    const res = await api.post("/found-report/send", formData);
    const data = res.data;
    if (data.details?.image) {
      data.details.image = `${BASE_URL}${data.details.image}`;
    }
    return data;
  } catch (error) {
    throw new Error(
      error.response?.data?.message || "فشل الارسال الرجاء المحاولة مرة أخرى",
    );
  }
};

export const validateUncertainSVC = async (matchId, decision) => {
  try {
    await api.post(`/report/${matchId}/validate`, {
      decision,
    });
  } catch (error) {
    throw { message: "Validation failed" };
  }
};
