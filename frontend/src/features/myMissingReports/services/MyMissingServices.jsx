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
    const res = await api.get("/my-uploaded-missings");
    const data = res.data;
    return data.map((item) => ({
      ...item,
      image: item.image ? `${BASE_URL}${item.image}` : null,
    }));
  } catch (error) {
    throw new Error("Getting the Missing Cases Failed");
  }
};

export const deleteMissing = async (id) => {
  console.log("Deleting missing case with ID:", id);
  return;
  try {
    await api.delete(`/my-uploaded-missings/${id}`);
  } catch (error) {
    throw new Error("Deleting the Missing Case Failed");
  }
};

export const updateMissing = async (id, updatedData) => {
  console.log("Updating missing case with ID:", id, "Data:", updatedData);
  return;
  try {
    await api.put(`/my-uploaded-missings/${id}`, updatedData);
  } catch (error) {
    const message =
      error.response?.data?.message || "حدث خطأ أثناء تحديث البلاغ";
    throw new Error(message);
  }
};
