import { useQuery } from "@tanstack/react-query";
import {
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Box,
  Chip,
  CircularProgress,
  Typography,
  LinearProgress,
} from "@mui/material";
import {
  CheckCircle as CompletedIcon,
  Error as ErrorIcon,
  Pending as PendingIcon,
  PlayArrow as RunningIcon,
  Pause as PausedIcon,
  Cancel as CancelledIcon,
} from "@mui/icons-material";
import { format } from "date-fns";
import { es } from "date-fns/locale";

import { jobsApi } from "@/services/api";
import { JobStatus, type Job } from "@/types";

interface JobsListProps {
  statusFilter?: string[];
  onJobSelect: (jobId: string) => void;
  selectedJobId: string | null;
}

const statusConfig: Record<
  JobStatus,
  { icon: React.ReactElement; color: any; label: string }
> = {
  [JobStatus.PENDING]: {
    icon: <PendingIcon />,
    color: "default",
    label: "Pendiente",
  },
  [JobStatus.VALIDATING]: {
    icon: <PendingIcon />,
    color: "info",
    label: "Validando",
  },
  [JobStatus.RUNNING]: {
    icon: <RunningIcon />,
    color: "primary",
    label: "En ejecución",
  },
  [JobStatus.PAUSED]: {
    icon: <PausedIcon />,
    color: "warning",
    label: "Pausado",
  },
  [JobStatus.COMPLETED]: {
    icon: <CompletedIcon />,
    color: "success",
    label: "Completado",
  },
  [JobStatus.COMPLETED_WITH_ERRORS]: {
    icon: <ErrorIcon />,
    color: "warning",
    label: "Con errores",
  },
  [JobStatus.FAILED]: {
    icon: <ErrorIcon />,
    color: "error",
    label: "Fallido",
  },
  [JobStatus.CANCELLED]: {
    icon: <CancelledIcon />,
    color: "default",
    label: "Cancelado",
  },
};

export default function JobsList({
  statusFilter,
  onJobSelect,
  selectedJobId,
}: JobsListProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["jobs", statusFilter],
    queryFn: () => jobsApi.list({ limit: 50 }),
    refetchInterval: 5000, // Refrescar cada 5 segundos
  });

  if (isLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography color="error">Error al cargar jobs</Typography>
      </Box>
    );
  }

  // Filtrar jobs por estado
  const filteredJobs =
    data?.jobs.filter((job) =>
      statusFilter ? statusFilter.includes(job.status) : true
    ) || [];

  if (filteredJobs.length === 0) {
    return (
      <Box sx={{ p: 4, textAlign: "center" }}>
        <Typography color="text.secondary">
          No hay jobs en esta categoría
        </Typography>
      </Box>
    );
  }

  return (
    <List sx={{ width: "100%", bgcolor: "background.paper" }}>
      {filteredJobs.map((job: Job) => {
        const config = statusConfig[job.status];
        const isSelected = selectedJobId === job.id;
        const isActive = [JobStatus.RUNNING, JobStatus.VALIDATING].includes(
          job.status
        );

        return (
          <ListItem
            key={job.id}
            disablePadding
            secondaryAction={
              <Chip
                icon={config.icon}
                label={config.label}
                color={config.color}
                size="small"
              />
            }
          >
            <ListItemButton
              selected={isSelected}
              onClick={() => onJobSelect(job.id)}
            >
              <ListItemIcon>{config.icon}</ListItemIcon>
              <ListItemText
                primary={
                  <>
                    <Typography variant="body1" noWrap>
                      {job.excel_file_name}
                    </Typography>
                    {isActive && (
                      <LinearProgress
                        variant="determinate"
                        value={job.progress_percentage}
                        sx={{ mt: 1, mb: 0.5 }}
                      />
                    )}
                  </>
                }
                secondary={
                  <>
                    <Typography variant="caption" display="block">
                      {format(new Date(job.created_at), "PPp", { locale: es })}
                    </Typography>
                    {isActive && (
                      <Typography variant="caption" color="primary">
                        {job.processed_records} / {job.total_records} registros
                        ({job.progress_percentage.toFixed(1)}%)
                      </Typography>
                    )}
                    {job.status === JobStatus.COMPLETED && (
                      <Typography variant="caption" color="success.main">
                        {job.successful_records} exitosos,{" "}
                        {job.total_files_downloaded} archivos
                      </Typography>
                    )}
                  </>
                }
              />
            </ListItemButton>
          </ListItem>
        );
      })}
    </List>
  );
}
