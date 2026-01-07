import { useQuery } from '@tanstack/react-query';
import { docuwareApi } from '@/services/api';

export const useCabinets = () => {
  return useQuery({
    queryKey: ['docuware-cabinets'],
    queryFn: docuwareApi.listCabinets,
  });
};

export const useDialogs = (cabinetId: string) => {
  return useQuery({
    queryKey: ['docuware-dialogs', cabinetId],
    queryFn: () => docuwareApi.listDialogs(cabinetId),
    enabled: !!cabinetId,
  });
};

export const useFields = (cabinetId: string) => {
  return useQuery({
    queryKey: ['docuware-fields', cabinetId],
    queryFn: () => docuwareApi.listFields(cabinetId),
    enabled: !!cabinetId,
  });
};
