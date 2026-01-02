// Componentes temporales hasta que los implementemos completamente
import {
  Box,
  Typography,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
} from "@mui/material";

// JobDetails - Detalles del Job
export function JobDetails({ jobId }: { jobId: string; onClose: () => void }) {
  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Detalles del Job
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Job ID: {jobId}
      </Typography>
      <Box sx={{ mt: 2 }}>
        <Typography variant="body2">Este componente mostrará:</Typography>
        <ul>
          <li>Progreso en tiempo real</li>
          <li>Estadísticas del job</li>
          <li>Logs de ejecución</li>
          <li>Controles (pausar, cancelar, reiniciar)</li>
        </ul>
      </Box>
    </Paper>
  );
}

// CreateJobWizard - Wizard para crear jobs
export function CreateJobWizard({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
  onJobCreated: (jobId: string) => void;
}) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Crear Nuevo Job</DialogTitle>
      <DialogContent>
        <Typography>Este wizard guiará al usuario a través de:</Typography>
        <ol>
          <li>Subir archivo Excel</li>
          <li>Seleccionar Cabinet y Dialog de DocuWare</li>
          <li>Mapear columnas Excel → Campos DocuWare</li>
          <li>Configurar transformaciones y estructura de carpetas</li>
          <li>Modo de prueba y ejecución</li>
        </ol>
      </DialogContent>
    </Dialog>
  );
}
