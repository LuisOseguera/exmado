import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { jobsApi } from '@/services/api';
import { JobStatus } from '@/types';

// Hook para listar jobs
export const useJobsList = (params?: {
  skip?: number;
  limit?: number;
  status_filter?: string;
  user_filter?: string;
}) => {
  return useQuery({
    queryKey: ['jobs', 'list', params],
    queryFn: () => jobsApi.list(params),
    refetchInterval: 5000,
  });
};

// Hook para obtener detalles de un job
export const useJobDetails = (jobId: string) => {
  return useQuery({
    queryKey: ['job', jobId],
    queryFn: () => jobsApi.get(jobId),
    enabled: !!jobId,
    refetchInterval: 3000,
  });
};

// Hook para obtener los logs de un job
export const useJobLogs = (jobId: string) => {
  return useQuery({
    queryKey: ['job-logs', jobId],
    queryFn: () => jobsApi.getLogs(jobId, { limit: 100 }),
    enabled: !!jobId,
    refetchInterval: 5000,
  });
};

// Hook (mutación) para iniciar un job
export const useStartJobMutation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (jobId: string) => jobsApi.start(jobId),
    onSuccess: (_, jobId) => {
      queryClient.invalidateQueries({ queryKey: ['job', jobId] });
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    },
  });
};

// Hook (mutación) para actualizar un job
export const useUpdateJobMutation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      jobId,
      status,
    }: {
      jobId: string;
      status: JobStatus;
    }) => jobsApi.update(jobId, { status }),
    onSuccess: (_, { jobId }) => {
      queryClient.invalidateQueries({ queryKey: ['job', jobId] });
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    },
  });
};
