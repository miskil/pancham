import { get, post, patch } from "./client";

export const listVillages = () => get("/admin/villages");
export const getPreviewToken = (id) => post(`/admin/villages/${id}/preview-token`);
export const onboardVillage = (body) => post("/admin/villages", body);
export const deactivateVillage = (id) => patch(`/admin/villages/${id}/deactivate`);
export const getVillageEvidence = (id) => get(`/admin/villages/${id}/evidence`);

export const listProposals = () => get("/admin/proposals");
export const getProposal = (id) => get(`/admin/proposals/${id}`);
export const reviewProposal = (id, notes) => patch(`/admin/proposals/${id}/review`, { notes });
export const acceptProposal = (id, notes) => patch(`/admin/proposals/${id}/accept`, { notes });
export const requestAmendment = (id, notes) => patch(`/admin/proposals/${id}/request-amendment`, { notes });
export const declineProposal = (id, notes) => patch(`/admin/proposals/${id}/decline`, { notes });

export const listPlans = () => get("/admin/plans");
export const getPlan = (id) => get(`/admin/plans/${id}`);
export const updatePlan = (id, plan_data) => patch(`/admin/plans/${id}`, { plan_data });
export const getWipPlan = (id) => get(`/admin/plans/${id}/wip`);
export const acceptPlan = (id) => patch(`/admin/plans/${id}/accept`);

export const listStatusUpdates = (villageId) => get(`/admin/status-updates${villageId ? `?village_id=${villageId}` : ""}`);
export const publishUpdate = (id) => patch(`/admin/status-updates/${id}/publish`);
export const unpublishUpdate = (id) => patch(`/admin/status-updates/${id}/unpublish`);
