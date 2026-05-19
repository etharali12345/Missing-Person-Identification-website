import { api, BASE_URL } from "../../../api/axios";

export const getUserProfile = async () => {
  try {
    const res = await api.get("/user-profile");
    return res.data;
  } catch (error) {
    throw new Error("فشل استرجاع بيانات الحساب");
  }
};

export const updateUserProfile = async (updatedData) => {
  try {
    await api.put("/user-profile", updatedData);
  } catch (error) {
    throw new Error("فشل تحديث المستخدم، يرجى التحقق من البيانات");
  }
};
