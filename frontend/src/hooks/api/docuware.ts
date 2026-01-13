/**
 * Hooks de React Query para operaciones con DocuWare
 *
 * Este archivo contiene los hooks para interactuar con la API de DocuWare,
 * incluyendo listado de cabinets, diálogos y campos.
 */

import { useQuery } from '@tanstack/react-query';
import { docuwareApi } from '@/services/api';
import type { DocuWareCabinet, DocuWareDialog, DocuWareField } from '@/types';

// ====================================================================
// Query Keys
// ====================================================================
export const docuwareKeys = {
  all: ['docuware'] as const,
  connection: () => [...docuwareKeys.all, 'connection'] as const,
  cabinets: () => [...docuwareKeys.all, 'cabinets'] as const,
  dialogs: (cabinetId: string) =>
    [...docuwareKeys.all, 'dialogs', cabinetId] as const,
  fields: (cabinetId: string) =>
    [...docuwareKeys.all, 'fields', cabinetId] as const,
};

// ====================================================================
// Query Hooks
// ====================================================================

/**
 * Hook para probar la conexión con DocuWare
 */
export const useDocuWareConnection = () => {
  return useQuery({
    queryKey: docuwareKeys.connection(),
    queryFn: () => docuwareApi.testConnection(),
    // Solo intentar una vez al montar el componente
    retry: 1,
    // No refrescar automáticamente
    refetchOnWindowFocus: false,
  });
};

/**
 * Hook para obtener la lista de cabinets
 */
export const useCabinets = () => {
  return useQuery<{ cabinets: DocuWareCabinet[]; total: number }>({
    queryKey: docuwareKeys.cabinets(),
    queryFn: async () => {
      const response = await docuwareApi.listCabinets();
      return response;
    },
    // Cachear por 5 minutos ya que los cabinets no cambian frecuentemente
    staleTime: 5 * 60 * 1000,
  });
};

/**
 * Hook para obtener los diálogos de un cabinet
 */
export const useDialogs = (cabinetId: string | null) => {
  return useQuery<{ dialogs: DocuWareDialog[]; total: number }>({
    queryKey: docuwareKeys.dialogs(cabinetId!),
    queryFn: async () => {
      const response = await docuwareApi.listDialogs(cabinetId!);
      return response;
    },
    enabled: !!cabinetId, // Solo ejecutar si tenemos un cabinetId
    staleTime: 5 * 60 * 1000,
  });
};

/**
 * Hook para obtener los campos de un cabinet
 */
export const useFields = (cabinetId: string | null) => {
  return useQuery<{ fields: DocuWareField[]; total: number }>({
    queryKey: docuwareKeys.fields(cabinetId!),
    queryFn: async () => {
      const response = await docuwareApi.listFields(cabinetId!);
      return response;
    },
    enabled: !!cabinetId, // Solo ejecutar si tenemos un cabinetId
    staleTime: 5 * 60 * 1000,
  });
};
