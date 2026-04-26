import axios from "axios";
import { Phone } from "lucide-react";

const BASE_URL = "http://localhost:5000";

const api = axios.create({
  baseURL: `${BASE_URL}/api`,
  withCredentials: true,
});

const profiles = [
  {
    id: 1,
    image_path: "images/found_123.jpg",
    full_name: "أحمد محمداحمد",
    age: 28,
    gender: "male",
    last_seen_date: "2024-01-15",
    last_seen_location: "الرياض، حي النزهة",
    phone_number1: "0501234567",
    phone_number2: "0559876543",
    status: "match",
    matchId: 53254,
  },
  {
    id: 2,
    image_path: "images/found_456.jpg",
    full_name: "فاطمة علي",
    age: 35,
    gender: "female",
    last_seen_date: "2024-02-20",
    last_seen_location: "جدة، حي الروضة",
    phone_number1: "0501234567",
    phone_number2: "0559876543",
    status: "nomatch",
  },
  {
    id: 3,
    image_path: "images/found_789.jpg",
    full_name: "خالد العمري",
    age: 42,
    gender: "male",
    last_seen_date: "2024-03-05",
    last_seen_location: "مكة المكرمة، حي العزيزية",
    phone_number1: "0501234567",
    phone_number2: "0559876543",
    status: "match",
    matchId: 98765,
  },
  {
    id: 4,
    image_path: "images/found_456.jpg",
    full_name: "نورة السعيد",
    age: 22,
    gender: "female",
    last_seen_date: "2024-03-10",
    last_seen_location: "الدمام، حي الشاطئ",
    phone_number1: "0501234567",
    phone_number2: "0559876543",
    status: "nomatch",
  },
];

export const getMissings = async () => {
  return profiles;
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
  console.log("Deleting missing case with ID:", id);
  return;
  try {
    await api.delete(`/my-missing-cases/${id}`);
  } catch (error) {
    throw new Error("Deleting the Missing Case Failed");
  }
};

export const updateMissing = async (id, updatedData) => {
  console.log("Updating missing case with ID:", id, "Data:", updatedData);
  return;
  try {
    await api.put(`/my-missing-cases/${id}`, updatedData);
  } catch (error) {
    const message =
      error.response?.data?.message || "حدث خطأ أثناء تحديث البلاغ";
    throw new Error(message);
  }
};

const details = {
  percentage: 0.85,
  full_name: "احمد محمد احمد",
  approximate_age: 34,
  gender: "male",
  health_status: "سليم",
  found_date: "2024-2-5",
  found_location: "الخرطوم الرياض",
  image_path: "images/found_123.jpg",
  authority_name: "منظمة الهلال الاحمر",
  phone_number1: "06546546456",
  phone_number2: "645654654654654645",
};

export const getMatchDetails = async (matchId) => {
  console.log("Fetching match details for ID:", matchId);
  return details;
  try {
    const res = await api.get(`/missing-match/${matchId}`);
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
