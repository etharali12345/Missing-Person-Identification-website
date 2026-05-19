import { api } from "../api/axios";

export const getMeService = async () => {
  try {
    const res = await api.get("/auth/me");
    return res.data.user;
    console.log("user is returned:", res.data.user);
  } catch (error) {
    console.log("An error occurr: ", error.response?.data);
    return null;
  }
};

export const loginService = async (email_or_phone, password) => {
  try {
    const res = await api.post("/auth/login", {
      email_or_phone,
      password,
    });
    return res.data.user;
  } catch (error) {
    throw new Error(error.response?.data?.message || "بيانات الدخول غير صحيحة");
  }
};

export const singupService = async (data) => {
  const isFormData = data instanceof FormData;
  try {
    const res = await api.post("/auth/signup", data, {
      headers: isFormData ? { "Content-Type": "multipart/form-data" } : {},
    });
    return res.data.user;
  } catch (error) {
    throw new Error(error.response?.data?.message || "فشل التسجيل");
  }
};

export const logoutService = async () => {
  try {
    await api.post("/auth/logout");
  } catch (error) {
    console.error("Logout failed on server", error);
  }
};
