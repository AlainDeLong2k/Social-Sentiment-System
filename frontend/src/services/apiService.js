import axios from "axios";

// Create a single, configured instance of axios.
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Fetches the latest weekly analysis results.
 * @returns {Promise<Array>} A promise that resolves to an array of weekly trend objects.
 */
export const getWeeklyTrends = async () => {
  try {
    const response = await apiClient.get("/trends/weekly");
    return response.data;
  } catch (error) {
    console.error(
      "Error fetching weekly trends:",
      error.response?.data?.detail || error.message
    );
    throw error;
  }
};

/**
 * Fetches the detailed analysis for a specific entity.
 * @param {string} entityId The ID of the entity.
 * @returns {Promise<Object>} A promise that resolves to the detailed trend object.
 */
export const getTrendDetail = async (entityId) => {
  try {
    const response = await apiClient.get(`/trends/${entityId}`);
    return response.data;
  } catch (error) {
    console.error(
      `Error fetching detail for entity ${entityId}:`,
      error.response?.data?.detail || error.message
    );
    throw error;
  }
};

/**
 * Starts a new on-demand analysis job.
 * @param {string} keyword The keyword to analyze.
 * @returns {Promise<Object>} A promise that resolves to an object containing the job ID.
 */
export const startOnDemandAnalysis = async (keyword) => {
  try {
    const response = await apiClient.post("/trends/analysis/on-demand", {
      keyword,
    });
    return response.data;
  } catch (error) {
    console.error(
      "Error starting on-demand analysis:",
      error.response?.data?.detail || error.message
    );
    throw error;
  }
};

/**
 * Checks the status of an on-demand analysis job.
 * @param {string} jobId The ID of the job to check.
 * @returns {Promise<Object>} A promise that resolves to the job status object.
 */
export const getJobStatus = async (jobId) => {
  try {
    const response = await apiClient.get(`/trends/analysis/status/${jobId}`);
    return response.data;
  } catch (error) {
    console.error(
      `Error fetching status for job ${jobId}:`,
      error.response?.data?.detail || error.message
    );
    throw error;
  }
};
