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
  public client: AxiosInstance;

  constructor(baseURL: string = 'http://localhost:9123') {
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
    // Only include language parameter if it's a non-empty string
    const params: any = { query };
    if (language && language.trim()) {
      params.language = language;
    }
    const response = await this.client.get('/api/glossary/search', { params });
    return response.data;
  }

  async getGlossaryCount(params?: {
    language?: string;
    source?: string;
    validation_status?: string;
  }): Promise<{ total: number }> {
    const response = await this.client.get('/api/glossary/count', { params });
    return response.data;
  }

  async exportGlossary(
    format: 'csv' | 'excel' | 'json',
    params?: {
      language?: string;
      source?: string;
      validation_status?: string;
    }
  ): Promise<Blob> {
    const response = await this.client.get('/api/glossary/export', {
      params: { ...params, format },
      responseType: 'blob',
    });
    return response.data;
  }

  async bulkUpdateEntries(
    entryIds: number[],
    validationStatus: 'pending' | 'validated' | 'rejected'
  ): Promise<{ message: string; updated_count: number; validation_status: string }> {
    const response = await this.client.post('/api/glossary/bulk-update', null, {
      params: {
        entry_ids: entryIds,
        validation_status: validationStatus,
      },
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

  async uploadDocumentsBatch(files: File[]): Promise<any> {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    const response = await this.client.post('/api/documents/upload-batch', formData, {
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

  async updateDocument(
    id: number,
    data: {
      document_number?: string;
      document_type_id?: number;
      document_link?: string;
    }
  ): Promise<UploadedDocument> {
    const response = await this.client.put(`/api/documents/${id}`, data);
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

  // FTS5 Full-Text Search Endpoints
  async searchFulltext(params: {
    q: string;
    language?: string;
    domain?: string;
    limit?: number;
    offset?: number;
  }): Promise<{
    query: string;
    total_results: number;
    results: Array<{
      id: number;
      term: string;
      definitions: any[];
      language: string;
      source: string;
      domain_tags: string[];
      relevance_score: number;
      snippet: string | null;
    }>;
    filters_applied: {
      language: string | null;
      domain: string | null;
      limit: number;
      offset: number;
    };
  }> {
    const response = await this.client.get('/api/search/fulltext', { params });
    return response.data;
  }

  async searchSuggest(params: {
    q: string;
    language?: string;
    limit?: number;
  }): Promise<{
    query: string;
    suggestions: string[];
  }> {
    const response = await this.client.get('/api/search/suggest', { params });
    return response.data;
  }

  async searchStats(): Promise<{
    fts5_enabled: boolean;
    total_indexed_entries: number;
    entries_by_language: Record<string, number>;
    top_sources: Record<string, number>;
    search_features: {
      porter_stemming: boolean;
      diacritic_removal: boolean;
      phrase_search: boolean;
      wildcard_search: boolean;
      boolean_operators: boolean;
      bm25_ranking: boolean;
      snippet_extraction: boolean;
    };
  }> {
    const response = await this.client.get('/api/search/stats');
    return response.data;
  }

  // Relationships Endpoints (Phase C: NLP Extraction & Graph Visualization)
  async getRelationships(params?: {
    source_term_id?: number;
    target_term_id?: number;
    relation_type?: string;
    min_confidence?: number;
    validated?: string;
    skip?: number;
    limit?: number;
  }): Promise<any[]> {
    const response = await this.client.get('/api/relationships', { params });
    return response.data;
  }

  async getRelationship(id: number): Promise<any> {
    const response = await this.client.get(`/api/relationships/${id}`);
    return response.data;
  }

  async createRelationship(data: {
    source_term_id: number;
    target_term_id: number;
    relation_type: string;
    confidence?: number;
    evidence?: string;
    context?: string;
    extraction_method?: string;
  }): Promise<any> {
    const response = await this.client.post('/api/relationships', data);
    return response.data;
  }

  async updateRelationship(id: number, data: {
    relation_type?: string;
    confidence?: number;
    evidence?: string;
    context?: string;
    validated?: string;
  }): Promise<any> {
    const response = await this.client.put(`/api/relationships/${id}`, data);
    return response.data;
  }

  async deleteRelationship(id: number): Promise<void> {
    await this.client.delete(`/api/relationships/${id}`);
  }

  async getGraphData(params?: {
    term_id?: number;
    relation_types?: string[];
    min_confidence?: number;
    max_depth?: number;
    validated_only?: boolean;
    limit?: number;
  }): Promise<{
    nodes: Array<{
      id: number;
      label: string;
      term: string;
      language: string;
      definition_count: number;
      group?: string;
    }>;
    edges: Array<{
      id: string;
      source: number;
      target: number;
      type: string;
      weight: number;
      label: string;
    }>;
    stats: {
      node_count: number;
      edge_count: number;
      relationship_types: string[];
      avg_confidence: number;
    };
  }> {
    const response = await this.client.get('/api/relationships/graph/data', { params });
    return response.data;
  }

  async extractRelationships(termId: number): Promise<{
    message: string;
    relationships_found: number;
    relationships_created: number;
    relationships: any[];
  }> {
    const response = await this.client.post(`/api/relationships/extract/${termId}`);
    return response.data;
  }

  async getRelationshipStats(): Promise<{
    total_relationships: number;
    by_type: Record<string, number>;
    by_validation: Record<string, number>;
    avg_confidence: number;
    terms_with_relationships: number;
    total_terms: number;
    coverage_percent: number;
  }> {
    const response = await this.client.get('/api/relationships/stats/overview');
    return response.data;
  }

  // Admin Endpoints
  async resetDatabase(): Promise<{ message: string }> {
    const response = await this.client.delete('/api/admin/reset-database');
    return response.data;
  }

  async getDatabaseStats(): Promise<any> {
    const response = await this.client.get('/api/admin/stats');
    return response.data;
  }

  // DocumentType Management Endpoints
  async getDocumentTypes(): Promise<any[]> {
    const response = await this.client.get('/api/admin/document-types');
    return response.data;
  }

  async getDocumentType(id: number): Promise<any> {
    const response = await this.client.get(`/api/admin/document-types/${id}`);
    return response.data;
  }

  async createDocumentType(data: { code: string; label_en: string; label_de: string; description?: string }): Promise<any> {
    const response = await this.client.post('/api/admin/document-types', data);
    return response.data;
  }

  async updateDocumentType(id: number, data: { code?: string; label_en?: string; label_de?: string; description?: string }): Promise<any> {
    const response = await this.client.put(`/api/admin/document-types/${id}`, data);
    return response.data;
  }

  async deleteDocumentType(id: number): Promise<void> {
    await this.client.delete(`/api/admin/document-types/${id}`);
  }
}

export const apiClient = new ApiClient();
export default apiClient;
