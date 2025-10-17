// TypeScript types for Glossary App

export interface GlossaryEntry {
  id: number;
  term: string;
  definition: string;
  language: 'de' | 'en';
  source: 'internal' | 'NAMUR' | 'DIN' | 'ASME' | 'IEC' | 'IATE';
  source_document?: string;
  domain_tags?: string[];
  validation_status: 'pending' | 'validated' | 'rejected';
  sync_status: 'pending_sync' | 'synced' | 'sync_failed';
  creation_date: string;
  updated_at: string;
}

export interface GlossaryEntryCreate {
  term: string;
  definition: string;
  language: 'de' | 'en';
  source?: string;
  source_document?: string;
  domain_tags?: string[];
}

export interface GlossaryEntryUpdate {
  term?: string;
  definition?: string;
  language?: 'de' | 'en';
  source?: string;
  source_document?: string;
  domain_tags?: string[];
  validation_status?: 'pending' | 'validated' | 'rejected';
  sync_status?: 'pending_sync' | 'synced' | 'sync_failed';
}

export interface UploadedDocument {
  id: number;
  filename: string;
  file_path: string;
  file_size: number;
  upload_status: 'pending' | 'processing' | 'completed' | 'failed';
  uploaded_at: string;
  processed_at?: string;
  processing_metadata?: ProcessingMetadata;
}

export interface ProcessingMetadata {
  original_filename?: string;
  pages?: number;
  text_length?: number;
  terms_extracted?: number;
  terms_saved?: number;
  language?: string;
  source?: string;
  errors?: string[];
}

export interface DocumentProcessRequest {
  extract_terms?: boolean;
  auto_validate?: boolean;
  language?: 'de' | 'en';
  source?: string;
}

export interface DocumentProcessResponse {
  document_id: number;
  status: string;
  extracted_text_length: number;
  terms_extracted: number;
  terms_saved: number;
  processing_time_seconds: number;
  errors?: string[];
}

export interface ApiError {
  detail: string;
}
