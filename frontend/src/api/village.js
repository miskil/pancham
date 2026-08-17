import { get, post, patch, del, postForm, download } from "./client";

export const getMe = () => get("/village/me");
export const getOrg = () => get("/village/org");
export const updateOrg = (body) => patch("/village/org", body);
export const listFundingRounds = () => get("/village/funding-rounds");
export const updateFundingRound = (roundId, body) => patch(`/village/funding-rounds/${roundId}`, body);
export const uploadReceipt = (roundId, formData) => postForm(`/village/funding-rounds/${roundId}/receipt`, formData);

export const listMou = () => get("/village/mou");
export const updateMouNotes = (mouId, body) => patch(`/village/mou/${mouId}`, body);
export const uploadMouSignedDocument = (mouId, formData) => postForm(`/village/mou/${mouId}/signed-document`, formData);
export const downloadMouDraftDocument = (mouId) => download(`/village/mou/${mouId}/draft-document`, "GET");
export const downloadMouSignedDocument = (mouId) => download(`/village/mou/${mouId}/signed-document`, "GET");

export const getProposal = () => get("/village/proposal");
export const createProposal = (body) => post("/village/proposal", body);
export const updateProposal = (body) => patch("/village/proposal", body);

export const createPlan = (body) => post("/village/plan", body);
export const getBaseline = () => get("/village/plan/baseline");
export const updateBaseline = (body) => patch("/village/plan/baseline", body);
export const getWip = () => get("/village/plan/wip");
export const updateWip = (body) => patch("/village/plan/wip", body);

export const listUpdates = () => get("/village/status");
export const createUpdate = (body) => post("/village/status", body);

export const getThreadMessages = (updateId) => get(`/threads/${updateId}/messages`);
export const postThreadMessage = (updateId, message) => post(`/threads/${updateId}/messages`, { message });

export const getChannelMessages = (villageId) => get(`/channels/${villageId}/messages`);
export const postChannelMessage = (villageId, message) => post(`/channels/${villageId}/messages`, { message });

export const uploadMedia = (updateId, formData) => postForm(`/village/status/${updateId}/media`, formData);

export const listEvidence = () => get("/village/evidence");
export const uploadEvidence = (formData) => postForm("/village/evidence", formData);
export const deleteEvidence = (id) => del(`/village/evidence/${id}`);

export const exportProposal = (id) => download(`/admin/export/proposals/${id}`, "POST");
export const exportPlan = (id) => download(`/admin/export/plans/${id}`, "POST");

export const listAnubhavPosts = () => get("/anubhav/posts");
export const createAnubhavPost = (body) => post("/anubhav/posts", body);
export const updateAnubhavPost = (id, body) => patch(`/anubhav/posts/${id}`, body);
export const deleteAnubhavPost = (id) => del(`/anubhav/posts/${id}`);
export const uploadAnubhavMedia = (id, formData) => postForm(`/anubhav/posts/${id}/media`, formData);
