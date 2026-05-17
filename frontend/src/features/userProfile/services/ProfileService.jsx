import axios from "axios";
import { Phone } from "lucide-react";

const BASE_URL = "http://localhost:5000";

const api = axios.create({
  baseURL: `${BASE_URL}/api`,
  withCredentials: true,
});

export const getUserProfile = async () => {
  return {
    first_name: "ahmed",
    last_name: "ali",
    email_or_phone: "54353535",
  };
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
