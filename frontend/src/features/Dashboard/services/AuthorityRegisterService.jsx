import axios from "axios";

const BASE_URL = "http://localhost:5000";

const api = axios.create({
  baseURL: `${BASE_URL}/api`,
  withCredentials: true,
});

export const getAuthoritiesSVC = async () => {
  try {
    const res = await api.get("/authorities");
    const data = res.data;
    return data;
  } catch (error) {
    const message =
      error.response?.data?.message || "حدث خطأ أثناء جلب طلبات التسجيل";
    throw new Error(message);
  }
};

export const getAuthorityByIdSVC = async (authorityId) => {
  try {
    const res = await api.get(`/authorities/${authorityId}`);
    const data = res.data;
    return {
      ...data,
      document: data.document ? `${BASE_URL}/${data.document}` : null,
    };
  } catch (error) {
    const message =
      error.response?.data?.message || "حدث خطأ أثناء جلب طلبات التسجيل";
    throw new Error(message);
  }
};

export const updateAuthorityStatus = async (authorityId, status) => {
  try {
    await api.patch(`/authorities/${authorityId}/status`, { status });
  } catch (error) {
    const message =
      error.response?.data?.message || "حدث خطأ أثناء تحديث حالة الطلب";
    throw new Error(message);
  }
};
