import axios from "axios";

const BASE_URL = "http://localhost:5000";

const api = axios.create({
  baseURL: `${BASE_URL}/api`,
  withCredentials: true,
});

const data = [
  {
    authority_id: 1,
    authority_type: "service",
    authority_name: "خدمة الإسعاف الوطني",
    email_or_phone: "ambulance@national.sa",
    location: "الرياض، المملكة العربية السعودية",
    document: "uploads/docs/doc1.pdf",
    license_number: "LIC-2024-001",
    status: "pending",
    created_at: "2024-11-01T08:30:00",
  },
  {
    authority_id: 2,
    authority_type: "organization",
    authority_name: "جمعية الهلال الأحمر",
    email_or_phone: "info@redcrescent.sa",
    location: "جدة، المملكة العربية السعودية",
    document: "uploads/docs/doc2.pdf",
    license_number: "LIC-2024-002",
    status: "approved",
    created_at: "2024-11-05T10:00:00",
  },
  {
    authority_id: 3,
    authority_type: "service",
    authority_name: "شركة أمن المدينة",
    email_or_phone: "security@madina.sa",
    location: "المدينة المنورة، المملكة العربية السعودية",
    document: "uploads/docs/doc3.pdf",
    license_number: "LIC-2024-003",
    status: "rejected",
    created_at: "2024-11-10T14:15:00",
  },
  {
    authority_id: 4,
    authority_type: "organization",
    authority_name: "منظمة دعم المجتمع",
    email_or_phone: "support@community.sa",
    location: "الدمام، المملكة العربية السعودية",
    document: null,
    license_number: "LIC-2024-004",
    status: "pending",
    created_at: "2024-11-12T09:45:00",
  },
];

export const getAuthoritiesSVC = async () => {
  return data;
  try {
    const res = await api.get("/authorities");
    const data = res.data;
    return data.map((authority) => ({
      ...authority,
      document: authority.document ? `${BASE_URL}/${authority.document}` : null,
    }));
  } catch (error) {
    const message =
      error.response?.data?.message || "حدث خطأ أثناء جلب طلبات التسجيل";
    throw new Error(message);
  }
};

export const updateAuthorityStatus = async (authorityId, status) => {
  console.log(`Updating authority ${authorityId} to status: ${status}`);
  return;
  try {
    await api.patch(`/authorities/${authorityId}/status`, { status });
  } catch (error) {
    const message =
      error.response?.data?.message || "حدث خطأ أثناء تحديث حالة الطلب";
    throw new Error(message);
  }
};
