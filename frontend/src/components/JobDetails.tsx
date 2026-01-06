import { useState } from 'react';
import {
  Paper,
  Box,
  Typography,
  LinearProgress,
  Button,
  IconButton,
  Chip,
  Grid,
  Card,
  CardContent,
  Divider,
  Alert,
  List,
  ListItem,
  ListItemText,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Close as CloseIcon,
  PlayArrow as StartIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Info as InfoIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { useSnackbar } from 'notistack';

import { useJobProgress } from '../hooks/useJobProgress';
import {
  useJobDetails,
  useJobLogs,
  useStartJobMutation,
  useUpdateJobMutation,
} from '../hooks/api/jobs';
import { JobStatus, JobLog, LogLevel } from '../types';

interface JobDetailsProps {
  jobId: string;
  onClose: () => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ py: 2 }}>{children}</Box>}
    </div>
  );
}

export default function JobDetails({ jobId, onClose }: JobDetailsProps) {
  const [activeTab, setActiveTab] = useState(0);
  const [confirmDialog, setConfirmDialog] = useState<{
    open: boolean;
    action: 'pause' | 'cancel' | null;
  }>({ open: false, action: null });

  const { enqueueSnackbar } = useSnackbar();

  const { data: job, isLoading } = useJobDetails(jobId);
  const { data: logsData } = useJobLogs(jobId);
  const { progress, isConnected } = useJobProgress(jobId);

  const startMutation = useStartJobMutation();
  const updateMutation = useUpdateJobMutation();

  if (isLoading || !job) {
    return (
      <Paper sx={{ p: 3 }}>
        <LinearProgress />
      </Paper>
    );
  }

  const isRunning = job.status === JobStatus.RUNNING;
  const isPending = job.status === JobStatus.PENDING;
  const isCompleted = [
    JobStatus.COMPLETED,
    JobStatus.COMPLETED_WITH_ERRORS,
    JobStatus.FAILED,
    JobStatus.CANCELLED,
  ].includes(job.status);

  const handleAction = (action: 'start' | 'pause' | 'cancel') => {
    if (action === 'start') {
      startMutation.mutate(jobId, {
        onSuccess: () =>
          enqueueSnackbar('Job iniciado exitosamente', { variant: 'success' }),
      });
    } else {
      setConfirmDialog({ open: true, action });
    }
  };

  const handleConfirmAction = () => {
    const action = confirmDialog.action;
    if (action) {
      const newStatus =
        action === 'pause' ? JobStatus.PAUSED : JobStatus.CANCELLED;
      updateMutation.mutate(
        { jobId, status: newStatus },
        {
          onSuccess: () => {
            enqueueSnackbar('Job actualizado', { variant: 'success' });
            setConfirmDialog({ open: false, action: null });
          },
        }
      );
    }
  };

  return (
    <>
      <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Box
          sx={{
            p: 2,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" noWrap>
              {job.excel_file_name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              ID: {job.id}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            {isConnected && (
              <Chip
                label="En vivo"
                color="success"
                size="small"
                icon={<RefreshIcon />}
              />
            )}
            <IconButton onClick={onClose} size="small">
              <CloseIcon />
            </IconButton>
          </Box>
        </Box>

        <Divider />

        {/* Progress Bar */}
        {isRunning && (
          <Box sx={{ p: 2 }}>
            <Box
              sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}
            >
              <Typography variant="body2">
                {progress?.current_action || 'Procesando...'}
              </Typography>
              <Typography variant="body2" color="primary">
                {job.progress_percentage.toFixed(1)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={job.progress_percentage}
            />
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ mt: 0.5 }}
            >
              {job.processed_records} / {job.total_records} registros
            </Typography>
          </Box>
        )}

        {/* Action Buttons */}
        <Box sx={{ px: 2, pb: 2, display: 'flex', gap: 1 }}>
          {isPending && (
            <Button
              variant="contained"
              startIcon={<StartIcon />}
              onClick={() => handleAction('start')}
              disabled={startMutation.isPending}
            >
              Iniciar
            </Button>
          )}
          {isRunning && (
            <>
              <Button
                variant="outlined"
                startIcon={<PauseIcon />}
                onClick={() => handleAction('pause')}
                disabled={updateMutation.isPending}
              >
                Pausar
              </Button>
              <Button
                variant="outlined"
                color="error"
                startIcon={<StopIcon />}
                onClick={() => handleAction('cancel')}
                disabled={updateMutation.isPending}
              >
                Cancelar
              </Button>
            </>
          )}
          {isCompleted && (
            <Button variant="outlined" startIcon={<DownloadIcon />} disabled>
              Descargar Reporte
            </Button>
          )}
        </Box>

        <Divider />

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
            <Tab label="Resumen" />
            <Tab label="Logs" />
            <Tab label="Configuración" />
          </Tabs>
        </Box>

        {/* Tab Content */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {/* Resumen */}
          <TabPanel value={activeTab} index={0}>
            <Grid container spacing={2}>
              {/* Estadísticas */}
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography
                      color="text.secondary"
                      gutterBottom
                      variant="body2"
                    >
                      Total Registros
                    </Typography>
                    <Typography variant="h4">{job.total_records}</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography
                      color="text.secondary"
                      gutterBottom
                      variant="body2"
                    >
                      Procesados
                    </Typography>
                    <Typography variant="h4">
                      {job.processed_records}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ bgcolor: 'success.light' }}>
                  <CardContent>
                    <Typography
                      color="success.contrastText"
                      gutterBottom
                      variant="body2"
                    >
                      Exitosos
                    </Typography>
                    <Typography variant="h4" color="success.contrastText">
                      {job.successful_records}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card
                  sx={{
                    bgcolor: job.failed_records > 0 ? 'error.light' : undefined,
                  }}
                >
                  <CardContent>
                    <Typography
                      color={
                        job.failed_records > 0
                          ? 'error.contrastText'
                          : 'text.secondary'
                      }
                      gutterBottom
                      variant="body2"
                    >
                      Fallidos
                    </Typography>
                    <Typography
                      variant="h4"
                      color={
                        job.failed_records > 0
                          ? 'error.contrastText'
                          : 'inherit'
                      }
                    >
                      {job.failed_records}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              {/* Información */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Información del Job
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="text.secondary">
                          Usuario
                        </Typography>
                        <Typography variant="body1">{job.user_name}</Typography>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="text.secondary">
                          Estado
                        </Typography>
                        <Chip label={job.status} color="primary" size="small" />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="text.secondary">
                          Creado
                        </Typography>
                        <Typography variant="body1">
                          {format(new Date(job.created_at), 'PPpp', {
                            locale: es,
                          })}
                        </Typography>
                      </Grid>
                      {job.started_at && (
                        <Grid item xs={12} sm={6}>
                          <Typography variant="body2" color="text.secondary">
                            Iniciado
                          </Typography>
                          <Typography variant="body1">
                            {format(new Date(job.started_at), 'PPpp', {
                              locale: es,
                            })}
                          </Typography>
                        </Grid>
                      )}
                      {job.completed_at && (
                        <Grid item xs={12} sm={6}>
                          <Typography variant="body2" color="text.secondary">
                            Completado
                          </Typography>
                          <Typography variant="body1">
                            {format(new Date(job.completed_at), 'PPpp', {
                              locale: es,
                            })}
                          </Typography>
                        </Grid>
                      )}
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="text.secondary">
                          Directorio de Salida
                        </Typography>
                        <Typography
                          variant="body2"
                          sx={{ fontFamily: 'monospace' }}
                        >
                          {job.output_directory}
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>

              {/* Error */}
              {job.error_message && (
                <Grid item xs={12}>
                  <Alert severity="error" icon={<ErrorIcon />}>
                    <Typography variant="body2">{job.error_message}</Typography>
                  </Alert>
                </Grid>
              )}
            </Grid>
          </TabPanel>

          {/* Logs */}
          <TabPanel value={activeTab} index={1}>
            <List sx={{ bgcolor: 'background.paper' }}>
              {logsData?.logs.map((log: JobLog) => {
                const logIcon =
                  log.level === LogLevel.ERROR ? (
                    <ErrorIcon color="error" />
                  ) : log.level === LogLevel.WARNING ? (
                    <WarningIcon color="warning" />
                  ) : (
                    <InfoIcon color="info" />
                  );

                return (
                  <ListItem
                    key={log.id}
                    sx={{ borderLeft: 3, borderColor: 'divider', mb: 1 }}
                  >
                    <ListItemText
                      primary={
                        <Box
                          sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
                        >
                          {logIcon}
                          <Typography variant="body2">{log.message}</Typography>
                        </Box>
                      }
                      secondary={
                        <Typography variant="caption" color="text.secondary">
                          {format(new Date(log.timestamp), 'PPpp', {
                            locale: es,
                          })}
                          {log.excel_row_number &&
                            ` - Fila ${log.excel_row_number}`}
                        </Typography>
                      }
                    />
                  </ListItem>
                );
              })}
            </List>
          </TabPanel>

          {/* Configuración */}
          <TabPanel value={activeTab} index={2}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Configuración del Job
                </Typography>
                <pre style={{ overflow: 'auto', fontSize: '0.875rem' }}>
                  {JSON.stringify(job.config, null, 2)}
                </pre>
              </CardContent>
            </Card>
          </TabPanel>
        </Box>
      </Paper>

      {/* Confirm Dialog */}
      <Dialog
        open={confirmDialog.open}
        onClose={() => setConfirmDialog({ open: false, action: null })}
      >
        <DialogTitle>Confirmar Acción</DialogTitle>
        <DialogContent>
          <Typography>
            {confirmDialog.action === 'pause'
              ? '¿Estás seguro de que deseas pausar este job?'
              : '¿Estás seguro de que deseas cancelar este job? Esta acción no se puede deshacer.'}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setConfirmDialog({ open: false, action: null })}
          >
            Cancelar
          </Button>
          <Button
            onClick={handleConfirmAction}
            color={confirmDialog.action === 'cancel' ? 'error' : 'primary'}
            variant="contained"
            disabled={updateMutation.isPending}
          >
            Confirmar
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
