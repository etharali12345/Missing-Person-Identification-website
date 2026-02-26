import axios from "axios";
import { useState } from "react";

/*
 send: email, password
 get || post login:   user{role}, 200  (success) 
                      message, 401     (failed)
*/
const user = { user: { role: "authority" } };

const api = axios.create({
  baseURL: "http://localhost:5000/api",
  withCredentials: true,
});

export const getMeService = async () => {
  return null;
  try {
    const res = await api.get("/auth/me");
    return res.data.user;
  } catch (error) {
    return null;
  }
};

export const loginService = async (email_or_phone, password) => {
  console.log(email_or_phone, password);
  return user.user;
  try {
    const res = await api.post("/auth/login", {
      email_or_phone,
      password,
    });
    return res.data.user;
  } catch (error) {
    throw new Error(error.response?.data?.message || "فشل تسجيل الدخول");
  }
};

export const singupService = async (data) => {
  const isFormData = data instanceof FormData;

  if (isFormData) {
    console.log("FormData:", [...data.entries()]);
  } else {
    console.log("Regular Object:", data);
  }
  return user.user;

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
