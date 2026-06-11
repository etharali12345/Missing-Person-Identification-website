import { api, BASE_URL } from "../../../api/axios";
import { Phone } from "lucide-react";

export const getMissings = async () => {
  try {
    const res = await api.get("/my-missing-cases");
    const data = res.data;
    return data.map((item) => ({
      ...item,
      image_path: item.image_path ? `${BASE_URL}/${item.image_path}` : null,
    }));
  } catch (error) {
    throw new Error("Getting the Missing Cases Failed");
  }
};

export const deleteMissing = async (id) => {
  try {
    await api.delete(`/my-missing-cases/${id}`);
  } catch (error) {
    throw new Error("Deleting the Missing Case Failed");
  }
};

export const updateMissing = async (id, updatedData) => {
  try {
    await api.put(`/my-missing-cases/${id}`, updatedData);
  } catch (error) {
    const message =
      error.response?.data?.message || "حدث خطأ أثناء تحديث البلاغ";
    throw new Error(message);
  }
};

export const getMatchDetails = async (matchId) => {
  try {
    const res = await api.get(`/my-missing-match/${matchId}`);
    const data = res.data;
    if (data?.image_path) {
      data.image_path = `${BASE_URL}/${data.image_path}`;
    }
    return data;
  } catch (error) {
    const message =
      error.response?.data?.message || "حدث خطأ أثناء جلب تفاصيل التطابق";
    throw new Error(message);
  }
};

export const confirmUncertainMatch = async (matchId) => {
  try {
    await api.patch(`/my-missing-match/${matchId}/confirm`);
  } catch (error) {
    const message =
      error.response?.data?.message || "حدث خطأ أثناء تأكيد التطابق";
    throw new Error(message);
  }
};

export const rejectUncertainMatch = async (matchId) => {
  try {
    await api.patch(`/my-missing-match/${matchId}/reject`);
  } catch (error) {
    const message =
      error.response?.data?.message || "حدث خطأ أثناء رفض التطابق";
    throw new Error(message);
  }
};
