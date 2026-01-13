/**
 * Hooks de React Query para operaciones con Jobs
 *
 * Este archivo encapsula todas las operaciones relacionadas con los trabajos
 * usando React Query. Esto nos da ventajas como:
 * - Cache automático de datos
 * - Revalidación en segundo plano
 * - Gestión automática de estados de carga/error
 * - Sincronización entre componentes
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { jobsApi } from '@/services/api';
import type {
  Job,
  JobListResponse,
  JobRecord,
  JobLogsResponse,
  CreateJobRequest,
  UpdateJobRequest,
} from '@/types';

// ====================================================================
// Query Keys - Identificadores únicos para las queries en el cache
// ====================================================================
export const jobsKeys = {
  all: ['jobs'] as const,
  lists: () => [...jobsKeys.all, 'list'] as const,
  list: (filters?: Record<string, unknown>) =>
    [...jobsKeys.lists(), filters] as const,
  details: () => [...jobsKeys.all, 'detail'] as const,
  detail: (id: string) => [...jobsKeys.details(), id] as const,
  records: (id: string) => [...jobsKeys.detail(id), 'records'] as const,
  logs: (id: string) => [...jobsKeys.detail(id), 'logs'] as const,
};

// ====================================================================
// Query Hooks - Para obtener datos (GET)
// ====================================================================

/**
 * Hook para obtener la lista de trabajos
 */
export const useJobsList = (params?: {
  skip?: number;
  limit?: number;
  status_filter?: string;
  user_filter?: string;
}) => {
  return useQuery<JobListResponse>({
    queryKey: jobsKeys.list(params),
    queryFn: () => jobsApi.list(params),
    // Revalidar cada 10 segundos si hay jobs activos
    refetchInterval: 10000,
  });
};

/**
 * Hook para obtener los detalles de un trabajo específico
 */
export const useJobDetails = (jobId: string | null) => {
  return useQuery<Job>({
    queryKey: jobsKeys.detail(jobId!),
    queryFn: () => jobsApi.get(jobId!),
    enabled: !!jobId, // Solo ejecutar si tenemos un jobId
    refetchInterval: 5000, // Refrescar cada 5 segundos
  });
};

/**
 * Hook para obtener los registros de un trabajo
 */
export const useJobRecords = (
  jobId: string | null,
  params?: {
    status_filter?: string;
    skip?: number;
    limit?: number;
  }
) => {
  return useQuery<JobRecord[]>({
    queryKey: jobsKeys.records(jobId!),
    queryFn: () => jobsApi.getRecords(jobId!, params),
    enabled: !!jobId,
  });
};

/**
 * Hook para obtener los logs de un trabajo
 */
export const useJobLogs = (
  jobId: string | null,
  params?: {
    level_filter?: string;
    skip?: number;
    limit?: number;
  }
) => {
  return useQuery<JobLogsResponse>({
    queryKey: jobsKeys.logs(jobId!),
    queryFn: () => jobsApi.getLogs(jobId!, params),
    enabled: !!jobId,
    refetchInterval: 5000, // Refrescar cada 5 segundos para ver logs nuevos
  });
};

// ====================================================================
// Mutation Hooks - Para modificar datos (POST, PATCH, DELETE)
// ====================================================================

/**
 * Hook para crear un nuevo trabajo
 */
export const useCreateJobMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (jobData: CreateJobRequest) => jobsApi.create(jobData),
    onSuccess: () => {
      // Invalidar la lista de jobs para que se recargue automáticamente
      queryClient.invalidateQueries({ queryKey: jobsKeys.lists() });
    },
  });
};

/**
 * Hook para actualizar un trabajo (pausar, reanudar, cancelar)
 */
export const useUpdateJobMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ jobId, ...updates }: UpdateJobRequest & { jobId: string }) =>
      jobsApi.update(jobId, updates),
    onSuccess: (_, variables) => {
      // Invalidar tanto la lista como los detalles del job específico
      queryClient.invalidateQueries({ queryKey: jobsKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: jobsKeys.detail(variables.jobId),
      });
    },
  });
};

/**
 * Hook para eliminar un trabajo
 */
export const useDeleteJobMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (jobId: string) => jobsApi.delete(jobId),
    onSuccess: () => {
      // Invalidar la lista de jobs
      queryClient.invalidateQueries({ queryKey: jobsKeys.lists() });
    },
  });
};

/**
 * Hook para iniciar un trabajo pendiente
 */
export const useStartJobMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (jobId: string) => jobsApi.start(jobId),
    onSuccess: (_, jobId) => {
      // Invalidar tanto la lista como los detalles del job
      queryClient.invalidateQueries({ queryKey: jobsKeys.lists() });
      queryClient.invalidateQueries({ queryKey: jobsKeys.detail(jobId) });
    },
  });
};
