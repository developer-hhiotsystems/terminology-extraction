// API client for backend integration
import axios, { AxiosInstance } from 'axios';
import type {
  GlossaryEntry,
  GlossaryEntryCreate,
  GlossaryEntryUpdate,
  UploadedDocument,
  DocumentProcessRequest,
  DocumentProcessResponse,
} from '../types';

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Glossary Endpoints
  async getGlossaryEntries(params?: {
    language?: string;
    source?: string;
    validation_status?: string;
    skip?: number;
    limit?: number;
  }): Promise<GlossaryEntry[]> {
    const response = await this.client.get('/api/glossary', { params });
    return response.data;
  }

  async getGlossaryEntry(id: number): Promise<GlossaryEntry> {
    const response = await this.client.get(`/api/glossary/${id}`);
    return response.data;
  }

  async createGlossaryEntry(entry: GlossaryEntryCreate): Promise<GlossaryEntry> {
    const response = await this.client.post('/api/glossary', entry);
    return response.data;
  }

  async updateGlossaryEntry(
    id: number,
    entry: GlossaryEntryUpdate
  ): Promise<GlossaryEntry> {
    const response = await this.client.put(`/api/glossary/${id}`, entry);
    return response.data;
  }

  async deleteGlossaryEntry(id: number): Promise<void> {
    await this.client.delete(`/api/glossary/${id}`);
  }

  async searchGlossary(query: string, language?: string): Promise<GlossaryEntry[]> {
    const response = await this.client.get('/api/glossary/search', {
      params: { query, language },
    });
    return response.data;
  }

  // Document Endpoints
  async uploadDocument(file: File): Promise<UploadedDocument> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async processDocument(
    documentId: number,
    params: DocumentProcessRequest
  ): Promise<DocumentProcessResponse> {
    const response = await this.client.post(
      `/api/documents/${documentId}/process`,
      params
    );
    return response.data;
  }

  async getDocuments(params?: {
    skip?: number;
    limit?: number;
  }): Promise<UploadedDocument[]> {
    const response = await this.client.get('/api/documents', { params });
    return response.data;
  }

  async getDocument(id: number): Promise<UploadedDocument> {
    const response = await this.client.get(`/api/documents/${id}`);
    return response.data;
  }

  async deleteDocument(id: number): Promise<void> {
    await this.client.delete(`/api/documents/${id}`);
  }

  // Health Check
  async healthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const apiClient = new ApiClient();
export default apiClient;
