// Enums
export enum JobStatus {
  PENDING = "pending",
  VALIDATING = "validating",
  RUNNING = "running",
  PAUSED = "paused",
  COMPLETED = "completed",
  COMPLETED_WITH_ERRORS = "completed_with_errors",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

export enum RecordStatus {
  PENDING = "pending",
  SEARCHING = "searching",
  FOUND = "found",
  NOT_FOUND = "not_found",
  DOWNLOADING = "downloading",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
}

export enum LogLevel {
  DEBUG = "debug",
  INFO = "info",
  WARNING = "warning",
  ERROR = "error",
  CRITICAL = "critical",
}

// Interfaces
export interface SearchFieldMapping {
  excel_column: string;
  docuware_field: string;
}

export interface TransformRules {
  tif_to_pdf: boolean;
  rename_pattern?: string;
  lowercase_filenames: boolean;
}

export interface JobConfig {
  cabinet_name: string;
  cabinet_id?: string;
  dialog_id: string;
  search_fields: SearchFieldMapping[];
  file_filters: string[];
  transform_rules: TransformRules;
  folder_structure: string[];
  include_associated_docs: boolean;
  test_mode: boolean;
  test_mode_limit: number;
  auto_start?: boolean;
}

export interface Job {
  id: string;
  user_name: string;
  status: JobStatus;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  excel_file_name: string;
  output_directory: string;
  total_records: number;
  processed_records: number;
  successful_records: number;
  failed_records: number;
  total_files_downloaded: number;
  progress_percentage: number;
  success_rate: number;
  config: JobConfig;
  error_message: string | null;
}

export interface JobRecord {
  id: string;
  job_id: string;
  excel_row_number: number;
  excel_data: Record<string, any>;
  docuware_record_id: string | null;
  status: RecordStatus;
  started_at: string | null;
  completed_at: string | null;
  downloaded_files_count: number;
  downloaded_files: any[] | null;
  output_folder_path: string | null;
  error_message: string | null;
}

export interface JobLog {
  id: string;
  job_id: string;
  timestamp: string;
  level: LogLevel;
  message: string;
  record_id: string | null;
  excel_row_number: number | null;
  details: string | null;
}

export interface ExcelValidation {
  is_valid: boolean;
  total_rows: number;
  columns: string[];
  errors: string[];
  warnings: string[];
  preview: Record<string, any>[];
  file_name?: string;
  file_path?: string;
  file_size?: number;
}

export interface DocuWareCabinet {
  id: string;
  name: string;
  type: string;
}

export interface DocuWareDialog {
  id: string;
  display_name: string;
  type: string;
}

export interface DocuWareField {
  db_name: string;
  display_name: string;
  type: string;
  length?: number;
  is_required: boolean;
}

export interface JobProgressUpdate {
  type: "connected" | "progress" | "completed" | "error" | "heartbeat";
  job_id: string;
  status?: JobStatus;
  processed_records?: number;
  total_records?: number;
  progress_percentage?: number;
  current_action?: string;
  latest_log?: string;
  message?: string;
  error_message?: string;
}

// Request types
export interface CreateJobRequest {
  user_name: string;
  excel_file_name: string;
  output_directory: string;
  config: JobConfig;
}

export interface UpdateJobRequest {
  status?: JobStatus;
}

// Response types
export interface JobListResponse {
  jobs: Job[];
  total: number;
  page: number;
  page_size: number;
}

export interface JobLogsResponse {
  logs: JobLog[];
  total: number;
}
