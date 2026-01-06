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
  UploadedFile,
  DocuWareDocument,
} from '@/types';
import SnackbarUtils from '@/utils/snackbar';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para manejo de errores
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

// ===== Jobs =====

export const jobsApi = {
  // Listar jobs
  list: async (params?: {
    skip?: number;
    limit?: number;
    status_filter?: string;
    user_filter?: string;
  }): Promise<JobListResponse> => {
    const { data } = await api.get<JobListResponse>('/jobs', { params });
    return data;
  },

  // Obtener job por ID
  get: async (jobId: string): Promise<Job> => {
    const { data } = await api.get<Job>(`/jobs/${jobId}`);
    return data;
  },

  // Crear job
  create: async (jobData: CreateJobRequest): Promise<Job> => {
    const { data } = await api.post<Job>('/jobs', jobData);
    return data;
  },

  // Actualizar job
  update: async (jobId: string, updates: UpdateJobRequest): Promise<Job> => {
    const { data } = await api.patch<Job>(`/jobs/${jobId}`, updates);
    return data;
  },

  // Eliminar job
  delete: async (jobId: string): Promise<void> => {
    await api.delete(`/jobs/${jobId}`);
  },

  // Iniciar job
  start: async (jobId: string): Promise<Job> => {
    const { data } = await api.post<Job>(`/jobs/${jobId}/start`);
    return data;
  },

  // Obtener records de job
  getRecords: async (
    jobId: string,
    params?: {
      status_filter?: string;
      skip?: number;
      limit?: number;
    }
  ): Promise<JobRecord[]> => {
    const { data } = await api.get<JobRecord[]>(`/jobs/${jobId}/records`, {
      params,
    });
    return data;
  },

  // Obtener logs de job
  getLogs: async (
    jobId: string,
    params?: {
      level_filter?: string;
      skip?: number;
      limit?: number;
    }
  ): Promise<JobLogsResponse> => {
    const { data } = await api.get<JobLogsResponse>(`/jobs/${jobId}/logs`, {
      params,
    });
    return data;
  },
};

// ===== Excel =====

export const excelApi = {
  // Subir Excel
  upload: async (
    file: File,
    requiredColumns?: string[],
    sheetName?: string,
    sheetIndex?: number
  ): Promise<ExcelValidation> => {
    const formData = new FormData();
    formData.append('file', file);

    if (requiredColumns && requiredColumns.length > 0) {
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
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return data;
  },

  // Listar archivos subidos
  listUploads: async (): Promise<{ files: UploadedFile[] }> => {
    const { data } = await api.get<{ files: UploadedFile[] }>(
      '/excel/list-uploads'
    );
    return data;
  },

  // Obtener hojas de Excel
  getSheets: async (
    filename: string
  ): Promise<{ sheets: string[]; total_sheets: number }> => {
    const { data } = await api.get(`/excel/sheets/${filename}`);
    return data;
  },

  // Preview de Excel
  preview: async (
    filename: string,
    params?: {
      sheet_name?: string;
      sheet_index?: number;
      n_rows?: number;
    }
  ): Promise<{
    filename: string;
    total_rows: number;
    columns: string[];
    preview: Record<string, unknown>[];
  }> => {
    const { data } = await api.get(`/excel/preview/${filename}`, { params });
    return data;
  },

  // Eliminar archivo
  delete: async (filename: string): Promise<void> => {
    await api.delete(`/excel/uploads/${filename}`);
  },
};

// ===== DocuWare =====

export const docuwareApi = {
  // Test de conexión
  testConnection: async (): Promise<{
    status: string;
    message: string;
    server_url: string;
    username: string;
  }> => {
    const { data } = await api.get('/docuware/test-connection');
    return data;
  },

  // Obtener configuración
  getConfig: async (): Promise<{
    server_url: string;
    username: string;
    timeout: number;
    configured: boolean;
  }> => {
    const { data } = await api.get('/docuware/config');
    return data;
  },

  // Listar cabinets
  listCabinets: async (): Promise<{
    cabinets: DocuWareCabinet[];
    total: number;
  }> => {
    const { data } = await api.get('/docuware/cabinets');
    return data;
  },

  // Listar diálogos
  listDialogs: async (
    cabinetId: string
  ): Promise<{ dialogs: DocuWareDialog[]; total: number }> => {
    const { data } = await api.get(`/docuware/cabinets/${cabinetId}/dialogs`);
    return data;
  },

  // Listar campos
  listFields: async (
    cabinetId: string
  ): Promise<{ fields: DocuWareField[]; total: number }> => {
    const { data } = await api.get(`/docuware/cabinets/${cabinetId}/fields`);
    return data;
  },

  // Buscar documentos
  search: async (
    cabinetId: string,
    dialogId: string,
    searchParams: Record<string, unknown>
  ): Promise<{ documents: DocuWareDocument[]; total: number }> => {
    const { data } = await api.post('/docuware/search', {
      cabinet_id: cabinetId,
      dialog_id: dialogId,
      search_params: searchParams,
    });
    return data;
  },
};

export default api;
