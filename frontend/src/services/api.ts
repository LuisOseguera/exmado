/**
 * Módulo de Servicios de API (api.ts)
 *
 * Este archivo centraliza toda la comunicación con el backend. Utilizamos `axios`
 * para crear una instancia pre-configurada que nos facilita hacer peticiones HTTP.
 *
 * Aquí definimos la URL base de la API y un "interceptor" que maneja
 * automáticamente los errores de todas las peticiones, mostrando una notificación
 * al usuario. También agrupamos las funciones de la API por recurso (Jobs, Excel, etc.)
 * para mantener el código ordenado.
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
  UploadedFile,
  DocuWareDocument,
} from '@/types';
import SnackbarUtils from '@/utils/snackbar';

// Creamos una instancia de axios con configuraciones por defecto.
const api = axios.create({
  // La URL base para todas las peticiones. Esto nos permite no tener que
  // escribir '/api/v1' cada vez.
  baseURL: '/api/v1',
  // Si una petición tarda más de 30 segundos, la cancelamos.
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Este 'interceptor' es una pieza clave. Es como un vigilante que revisa
// todas las respuestas que llegan del servidor.
api.interceptors.response.use(
  // Si la respuesta fue exitosa (código 2xx), simplemente la dejamos pasar.
  (response) => response,
  // Si la respuesta trae un error...
  (error) => {
    // Intentamos sacar el mensaje de error que nos manda el backend.
    // Si no existe, usamos el mensaje de error general de la petición.
    const message = error.response?.data?.detail || error.message || 'Ocurrió un error inesperado.';

    // Usamos nuestro sistema de notificaciones para mostrarle el error al usuario.
    SnackbarUtils.error(message);

    // Es importante rechazar la promesa para que el código que hizo la llamada
    // (por ejemplo, en React Query) sepa que la petición falló.
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
    const { data } = await api.get<JobRecord[]>(`/jobs/${jobId}/records`, { params });
    return data;
  },

  /**
   * Obtiene los logs de ejecución de un trabajo.
   */
  getLogs: async (
    jobId: string,
    params?: { level_filter?: string; skip?: number; limit?: number }
  ): Promise<JobLogsResponse> => {
    const { data } = await api.get<JobLogsResponse>(`/jobs/${jobId}/logs`, { params });
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

    const { data } = await api.post<ExcelValidation>('/excel/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // ... (otros endpoints de excelApi)
};

// ====================================================================
// Endpoints relacionados con DocuWare
// ====================================================================
export const docuwareApi = {
  /**
   * Prueba la conexión con el servidor de DocuWare.
   */
  testConnection: async (): Promise<{ status: string; message: string; server_url: string; username: string; }> => {
    const { data } = await api.get('/docuware/test-connection');
    return data;
  },

  // ... (otros endpoints de docuwareApi)
};

export default api;
