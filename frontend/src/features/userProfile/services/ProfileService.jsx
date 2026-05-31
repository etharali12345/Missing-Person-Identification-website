import { api } from "../../../api/axios";

export const getUserProfile = async () => {
  try {
    const res = await api.get("/user-profile");
    return res.data;
  } catch (error) {
    throw new Error("فشل استرجاع بيانات الحساب");
  }
};

export const updateUserInfo = async (updatedData) => {
  try {
    await api.put("/user-profile/info", updatedData);
  } catch (error) {
    throw new Error(
      error.response?.data?.error ||
        "فشل تحديث البيانات، يرجى التحقق من المدخلات",
    );
  }
};

export const updateUserPassword = async (updatedData) => {
  try {
    await api.put("/user-profile/password", updatedData);
  } catch (error) {
    throw new Error(
      error.response?.data?.error ||
        "فشل تحديث كلمة المرور، يرجى التحقق من البيانات",
    );
  }
};
