const BASE_URL = 'https://vigilance-ai-backend.onrender.com/api/v1';
export const api = {
  async getStats() {
    const res = await fetch(`${BASE_URL}/stats`);
    return res.json();
  },
  async getDailyStats() {
    const res = await fetch(`${BASE_URL}/stats/daily`);
    return res.json();
  },
  async getCameraStats() {
    const res = await fetch(`${BASE_URL}/stats/cameras`);
    return res.json();
  },
  async getViolations(params = {}) {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${BASE_URL}/violations?${query}`);
    return res.json();
  },
  async getViolation(incidentId) {
    const res = await fetch(`${BASE_URL}/violations/${incidentId}`);
    return res.json();
  },
  async searchByPlate(plate) {
    const res = await fetch(`${BASE_URL}/violations/search/${plate}`);
    return res.json();
  },
  async analyzeImage(formData) {
    // Step 1: submit job, get job_id immediately
    const res = await fetch(`${BASE_URL}/analyze`, {
      method: 'POST',
      body: formData,
    });
    const { job_id } = await res.json();

    // Step 2: poll until done (max 3 minutes)
    const maxAttempts = 45;
    for (let i = 0; i < maxAttempts; i++) {
      await new Promise(r => setTimeout(r, 4000)); // wait 4s between polls
      const poll = await fetch(`${BASE_URL}/analyze/status/${job_id}`);
      const data = await poll.json();
      if (data.status === 'done') return data.result;
      if (data.status === 'error') throw new Error(data.detail || 'Analysis failed');
    }
    throw new Error('Analysis timed out after 3 minutes.');
  },
  async getChallans(params = {}) {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${BASE_URL}/challans?${query}`);
    return res.json();
  },
  async getChallanSummary() {
    const res = await fetch(`${BASE_URL}/challans/summary`);
    return res.json();
  },
  async issueChallan(incidentId) {
    const res = await fetch(`${BASE_URL}/challan/${incidentId}`, {
      method: 'POST',
    });
    return res.json();
  },
  async updateChallanStatus(challanId, status) {
    const res = await fetch(`${BASE_URL}/challan/${challanId}/status?status=${status}`, {
      method: 'PATCH',
    });
    return res.json();
  },
};
