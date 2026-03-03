import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5000/api",
  withCredentials: true,
});
/*{
  "status": "match",
  "confidence": 0.91,
  "person": {
    "name": "Ahmed Ali",
    "age": 14,
    "location": "Khartoum",
    "imageUrl": "/uploads/found_123.jpg"
  }
}*/
export const submitMissingReport = async (formData) => {
  return <></>;
};

export const validateMissingMatch = async (matchId, decision) => {
  try {
    const response = await api.post(`/missing-report/${matchId}/validate`, {
      decision,
    });

    return response.data;
  } catch (error) {
    throw error.response?.data || { message: "Validation failed" };
  }
};
