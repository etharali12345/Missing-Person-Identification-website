import { api, BASE_URL } from "../../../api/axios";

export const getFoundDB = async () => {
  try {
    const res = await api.get("/found-database");
    const data = res.data;
    return data.map((item) => ({
      ...item,
      image_path: item.image_path ? `${BASE_URL}/${item.image_path}` : null,
    }));
  } catch (error) {
    throw new Error("Getting the Found Database Entries Failed");
  }
};

export const getFoundById = async (id) => {
  try {
    const res = await api.get(`/found-database/${id}`);
    const data = res.data;
    return {
      ...data,
      image_path: data.image_path ? `${BASE_URL}/${data.image_path}` : null,
    };
  } catch (error) {
    throw new Error("Getting the Found Database Entries Failed");
  }
};

export const deleteFound = async (id) => {
  try {
    await api.delete(`/found-database/${id}`);
  } catch (error) {
    throw new Error("Deleting the Found Database Entry Failed");
  }
};

export const getMatchDetails = async (matchId) => {
  try {
    const res = await api.get(`/found-database-match/${matchId}`);
    const data = res.data;
    if (data?.image_path) {
      data.image_path = `${BASE_URL}/${data.image_path}`;
    }
    return data;
  } catch (error) {
    throw new Error("Getting Match of Found Failed");
  }
};

export const cancelMatch = async (matchId) => {
  try {
    await api.patch(`/found-database-match/${matchId}/cancel`);
  } catch (error) {
    throw new Error("Cancel Match of Found Failed");
  }
};
