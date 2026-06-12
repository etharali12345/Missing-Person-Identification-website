import { api, BASE_URL } from "../../../api/axios";

export const submitFoundReportSVC = async (formData) => {
  try {
    const res = await api.post("/found-report/send", formData);
    const data = res.data;
    if (data.details?.image_path) {
      data.details.image_path = `${BASE_URL}/${data.details.image_path}`;
    }
    return data;
  } catch (error) {
    throw new Error(
      error.response?.data?.message || "فشل الارسال الرجاء المحاولة مرة أخرى",
    );
  }
};

export const validateUncertainSVC = async (matchId, percentage, decision) => {
  try {
    await api.post(`/found-report/${matchId}/validate`, {
      matchId,
      percentage,
      decision,
    });
  } catch (error) {
    throw { message: "Validation failed" };
  }
};
