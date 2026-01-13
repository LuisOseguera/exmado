/**
 * Módulo de Servicios de API (api.ts)
 *
 * Este archivo centraliza toda la comunicación con el backend. Utilizamos `axios`
 * para crear una instancia pre-configurada que nos facilita hacer peticiones HTTP.
 */
import axios from 'axios';
import type {
  Job,
  JobListResponse,
  JobRecord,
  JobLogsResponse,
  CreateJobRequest,
  UpdateJobRequest,
  ExcelValidation,
  DocuWareCabinet,
  DocuWareDialog,
  DocuWareField,
} from '@/types';
import SnackbarUtils from '@/utils/snackbar';

// Creamos una instancia de axios con configuraciones por defecto.
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para manejar errores globalmente
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.message ||
      'Ocurrió un error inesperado.';
    SnackbarUtils.error(message);
    return Promise.reject(error);
  }
);

// ====================================================================
// Endpoints relacionados con los Trabajos (Jobs)
// ====================================================================
export const jobsApi = {
  /**
   * Obtiene una lista paginada y filtrada de trabajos.
   */
  list: async (params?: {
    skip?: number;
    limit?: number;
    status_filter?: string;
    user_filter?: string;
  }): Promise<JobListResponse> => {
    const { data } = await api.get<JobListResponse>('/jobs', { params });
    return data;
  },

  /**
   * Obtiene los detalles de un trabajo específico por su ID.
   */
  get: async (jobId: string): Promise<Job> => {
    const { data } = await api.get<Job>(`/jobs/${jobId}`);
    return data;
  },

  /**
   * Crea un nuevo trabajo.
   */
  create: async (jobData: CreateJobRequest): Promise<Job> => {
    const { data } = await api.post<Job>('/jobs', jobData);
    return data;
  },

  /**
   * Actualiza el estado de un trabajo.
   */
  update: async (jobId: string, updates: UpdateJobRequest): Promise<Job> => {
    const { data } = await api.patch<Job>(`/jobs/${jobId}`, updates);
    return data;
  },

  /**
   * Elimina un trabajo.
   */
  delete: async (jobId: string): Promise<void> => {
    await api.delete(`/jobs/${jobId}`);
  },

  /**
   * Inicia la ejecución de un trabajo pendiente.
   */
  start: async (jobId: string): Promise<Job> => {
    const { data } = await api.post<Job>(`/jobs/${jobId}/start`);
    return data;
  },

  /**
   * Obtiene los registros (filas del Excel) asociados a un trabajo.
   */
  getRecords: async (
    jobId: string,
    params?: { status_filter?: string; skip?: number; limit?: number }
  ): Promise<JobRecord[]> => {
    const { data } = await api.get<JobRecord[]>(`/jobs/${jobId}/records`, {
      params,
    });
    return data;
  },

  /**
   * Obtiene los logs de ejecución de un trabajo.
   */
  getLogs: async (
    jobId: string,
    params?: { level_filter?: string; skip?: number; limit?: number }
  ): Promise<JobLogsResponse> => {
    const { data } = await api.get<JobLogsResponse>(`/jobs/${jobId}/logs`, {
      params,
    });
    return data;
  },
};

// ====================================================================
// Endpoints relacionados con los archivos de Excel
// ====================================================================
export const excelApi = {
  /**
   * Sube un archivo de Excel para su validación.
   */
  upload: async (
    file: File,
    requiredColumns?: string[],
    sheetName?: string,
    sheetIndex?: number
  ): Promise<ExcelValidation> => {
    const formData = new FormData();
    formData.append('file', file);

    if (requiredColumns?.length) {
      formData.append('required_columns', requiredColumns.join(','));
    }
    if (sheetName) {
      formData.append('sheet_name', sheetName);
    }
    if (sheetIndex !== undefined) {
      formData.append('sheet_index', sheetIndex.toString());
    }

    const { data } = await api.post<ExcelValidation>(
      '/excel/upload',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return data;
  },

  /**
   * Valida un Excel existente en el servidor.
   */
  validate: async (
    filePath: string,
    requiredColumns?: string[],
    sheetName?: string,
    sheetIndex?: number
  ): Promise<ExcelValidation> => {
    const formData = new FormData();
    formData.append('file_path', filePath);

    if (requiredColumns?.length) {
      formData.append('required_columns', requiredColumns.join(','));
    }
    if (sheetName) {
      formData.append('sheet_name', sheetName);
    }
    if (sheetIndex !== undefined) {
      formData.append('sheet_index', sheetIndex.toString());
    }

    const { data } = await api.post<ExcelValidation>(
      '/excel/validate',
      formData
    );
    return data;
  },

  /**
   * Lista los archivos Excel subidos por el usuario.
   */
  listUploads: async (): Promise<{ files: unknown[] }> => {
    const { data } = await api.get('/excel/list-uploads');
    return data;
  },

  /**
   * Obtiene las hojas de un archivo Excel.
   */
  getSheets: async (
    filename: string
  ): Promise<{ filename: string; sheets: string[]; total_sheets: number }> => {
    const { data } = await api.get(`/excel/sheets/${filename}`);
    return data;
  },

  /**
   * Obtiene una vista previa de un archivo Excel.
   */
  preview: async (
    filename: string,
    params?: { sheet_name?: string; sheet_index?: number; n_rows?: number }
  ): Promise<{
    filename: string;
    total_rows: number;
    columns: string[];
    preview: Record<string, unknown>[];
  }> => {
    const { data } = await api.get(`/excel/preview/${filename}`, { params });
    return data;
  },
};

// ====================================================================
// Endpoints relacionados con DocuWare
// ====================================================================
export const docuwareApi = {
  /**
   * Prueba la conexión con el servidor de DocuWare.
   */
  testConnection: async (): Promise<{
    status: string;
    message: string;
    server_url: string;
    username: string;
  }> => {
    const { data } = await api.get('/docuware/test-connection');
    return data;
  },

  /**
   * Lista todos los file cabinets disponibles.
   */
  listCabinets: async (): Promise<{
    cabinets: DocuWareCabinet[];
    total: number;
  }> => {
    const { data } = await api.get('/docuware/cabinets');
    return data;
  },

  /**
   * Lista los diálogos de búsqueda de un cabinet.
   */
  listDialogs: async (
    cabinetId: string
  ): Promise<{
    dialogs: DocuWareDialog[];
    total: number;
    cabinet_id: string;
  }> => {
    const { data } = await api.get(`/docuware/cabinets/${cabinetId}/dialogs`);
    return data;
  },

  /**
   * Lista los campos de un cabinet.
   */
  listFields: async (
    cabinetId: string
  ): Promise<{
    fields: DocuWareField[];
    total: number;
    cabinet_id: string;
  }> => {
    const { data } = await api.get(`/docuware/cabinets/${cabinetId}/fields`);
    return data;
  },

  /**
   * Busca documentos en DocuWare.
   */
  searchDocuments: async (
    cabinetId: string,
    dialogId: string,
    searchParams: Record<string, unknown>
  ): Promise<{
    documents: unknown[];
    total: number;
    cabinet_id: string;
    dialog_id: string;
  }> => {
    const { data } = await api.post('/docuware/search', {
      cabinet_id: cabinetId,
      dialog_id: dialogId,
      search_params: searchParams,
    });
    return data;
  },

  /**
   * Obtiene información de un documento específico.
   */
  getDocument: async (
    cabinetId: string,
    documentId: string
  ): Promise<unknown> => {
    const { data } = await api.get(
      `/docuware/documents/${cabinetId}/${documentId}`
    );
    return data;
  },

  /**
   * Obtiene los documentos vinculados de un documento.
   */
  getDocumentLinks: async (
    cabinetId: string,
    documentId: string
  ): Promise<{ document_id: string; links: unknown[]; total: number }> => {
    const { data } = await api.get(
      `/docuware/documents/${cabinetId}/${documentId}/links`
    );
    return data;
  },

  /**
   * Obtiene la configuración actual de DocuWare.
   */
  getConfig: async (): Promise<{
    server_url: string;
    username: string;
    timeout: number;
    configured: boolean;
  }> => {
    const { data } = await api.get('/docuware/config');
    return data;
  },
};

export default api;
