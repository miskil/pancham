import { get } from "./client";

export const listVillages = () => get("/donor/villages");
export const getVillageUpdates = (id) => get(`/donor/villages/${id}/updates`);
