import axios from 'axios';

// Cloud Function Base URLs
const API_BASE_URLS = {
  ingestEvents: 'https://ingest-events-ev2z3eeafa-ue.a.run.app',
  generateReport: 'https://generate-va-report-ev2z3eeafa-ue.a.run.app',
  getMetrics: 'https://get-confluent-metrics-ev2z3eeafa-ue.a.run.app',
  getSoldierSummary: 'https://get-soldier-summary-ev2z3eeafa-ue.a.run.app',
  getHealthAlerts: 'https://get-health-alerts-ev2z3eeafa-ue.a.run.app',
  resolveAlert: 'https://resolve-alert-ev2z3eeafa-ue.a.run.app'
};

// Create axios instance with default config
const apiClient = axios.create({
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// API Service
const apiService = {
  // Get Health Alerts
  getHealthAlerts: async () => {
    try {
      const response = await apiClient.get(API_BASE_URLS.getHealthAlerts);
      return response.data;
    } catch (error) {
      console.error('Error fetching health alerts:', error);
      throw error;
    }
  },

  // Get Soldier Summary
  getSoldierSummary: async (soldierId) => {
    try {
      const response = await apiClient.get(`${API_BASE_URLS.getSoldierSummary}?soldier_id=${soldierId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching soldier summary:', error);
      throw error;
    }
  },

  // Generate VA Report
  generateVAReport: async (soldierId) => {
    try {
      const response = await apiClient.post(API_BASE_URLS.generateReport, {
        soldier_id: soldierId
      });
      return response.data;
    } catch (error) {
      console.error('Error generating VA report:', error);
      throw error;
    }
  },

  // Get Confluent Metrics
  getConfluentMetrics: async () => {
    try {
      const response = await apiClient.get(API_BASE_URLS.getMetrics);
      return response.data;
    } catch (error) {
      console.error('Error fetching Confluent metrics:', error);
      throw error;
    }
  },

  // Resolve Alert
  resolveAlert: async (alertId, resolution) => {
    try {
      const response = await apiClient.post(API_BASE_URLS.resolveAlert, {
        alert_id: alertId,
        resolution: resolution
      });
      return response.data;
    } catch (error) {
      console.error('Error resolving alert:', error);
      throw error;
    }
  }
};

export default apiService;