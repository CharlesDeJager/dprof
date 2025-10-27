import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // File operations
  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post('/upload-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Database operations
  async connectDatabase(connectionInfo) {
    const response = await this.client.post(
      '/connect-database',
      connectionInfo,
    );
    return response.data;
  }

  async getRecordCount(sessionId, tableName) {
    const response = await this.client.get(
      `/session/${sessionId}/record-count?table_name=${tableName}`,
    );
    return response.data;
  }

  // Profiling operations
  async startProfiling(profilingRequest) {
    const response = await this.client.post('/profile-data', profilingRequest);
    return response.data;
  }

  async getProfilingStatus(sessionId) {
    const response = await this.client.get(`/profiling-status/${sessionId}`);
    return response.data;
  }

  async getProfilingResults(sessionId) {
    const response = await this.client.get(`/profiling-results/${sessionId}`);
    return response.data;
  }

  // Export operations
  async exportResults(exportRequest) {
    const response = await this.client.post('/export', exportRequest, {
      responseType: 'blob',
    });
    return response.data;
  }

  // Settings
  async getSettings() {
    const response = await this.client.get('/settings');
    return response.data;
  }

  async updateSettings(settings) {
    const response = await this.client.post('/settings', settings);
    return response.data;
  }
}

export default new ApiService();
