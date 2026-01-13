import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Stepper,
  Step,
  StepLabel,
  Box,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  IconButton,
  Paper,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { useSnackbar } from 'notistack';
import { AxiosError } from 'axios';

import { jobsApi, excelApi } from '@/services/api';
import { useCabinets, useDialogs, useFields } from '@/hooks/api/docuware';
import type {
  CreateJobRequest,
  ExcelValidation,
  SearchFieldMapping,
} from '@/types';

interface CreateJobWizardProps {
  open: boolean;
  onClose: () => void;
  onJobCreated: (jobId: string) => void;
}

const steps = [
  'Subir Excel',
  'DocuWare',
  'Mapeo de Campos',
  'Configuración',
  'Resumen',
];

export default function CreateJobWizard({
  open,
  onClose,
  onJobCreated,
}: CreateJobWizardProps) {
  const [activeStep, setActiveStep] = useState(0);
  const { enqueueSnackbar } = useSnackbar();

  // Estado del formulario
  const [excelFile, setExcelFile] = useState<File | null>(null);
  const [excelValidation, setExcelValidation] =
    useState<ExcelValidation | null>(null);
  const [selectedCabinetId, setSelectedCabinetId] = useState('');
  const [selectedDialogId, setSelectedDialogId] = useState('');
  const [fieldMappings, setFieldMappings] = useState<SearchFieldMapping[]>([
    { excel_column: '', docuware_field: '' },
  ]);
  const [outputDirectory, setOutputDirectory] = useState('./output');
  const [fileFilters] = useState<string[]>(['pdf', 'tif']);
  const [tifToPdf, setTifToPdf] = useState(true);
  const [renamePattern, setRenamePattern] = useState('');
  const [folderStructure, setFolderStructure] = useState<string[]>([]);
  const [testMode, setTestMode] = useState(true);
  const [testModeLimit, setTestModeLimit] = useState(10);

  // Queries
  const { data: cabinetsData } = useCabinets();
  const { data: dialogsData } = useDialogs(selectedCabinetId);
  const { data: fieldsData } = useFields(selectedCabinetId);

  // Mutations
  const uploadMutation = useMutation({
    mutationFn: (file: File) => excelApi.upload(file),
    onSuccess: (data) => {
      setExcelValidation(data);
      if (data.is_valid) {
        enqueueSnackbar('Excel validado exitosamente', { variant: 'success' });
        setActiveStep(1);
      } else {
        enqueueSnackbar('Excel tiene errores', { variant: 'error' });
      }
    },
  });

  const createJobMutation = useMutation({
    mutationFn: (jobData: CreateJobRequest) => jobsApi.create(jobData),
    onSuccess: (data) => {
      enqueueSnackbar('Job creado exitosamente', { variant: 'success' });
      onJobCreated(data.id);
    },
    onError: (error: AxiosError<{ detail: string }>) => {
      enqueueSnackbar(
        `Error: ${error.response?.data?.detail || error.message}`,
        {
          variant: 'error',
        }
      );
    },
  });

  // Dropzone para Excel
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': [
        '.xlsx',
      ],
      'application/vnd.ms-excel': ['.xls'],
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setExcelFile(acceptedFiles[0]);
      }
    },
  });

  const handleNext = () => {
    if (activeStep === 0 && excelFile) {
      uploadMutation.mutate(excelFile);
    } else if (activeStep === 3) {
      // Validar configuración
      if (folderStructure.length === 0 && excelValidation?.columns) {
        setFolderStructure([excelValidation.columns[0]]);
      }
      setActiveStep(activeStep + 1);
    } else {
      setActiveStep(activeStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep(activeStep - 1);
  };

  const handleCreateJob = () => {
    if (!excelFile || !excelValidation) return;

    const jobData: CreateJobRequest = {
      user_name: 'usuario_actual',
      excel_file_name: excelFile.name,
      output_directory: outputDirectory,
      config: {
        cabinet_name:
          cabinetsData?.cabinets.find((c) => c.id === selectedCabinetId)
            ?.name || '',
        cabinet_id: selectedCabinetId,
        dialog_id: selectedDialogId,
        search_fields: fieldMappings.filter(
          (m) => m.excel_column && m.docuware_field
        ),
        file_filters: fileFilters,
        transform_rules: {
          tif_to_pdf: tifToPdf,
          rename_pattern: renamePattern || undefined,
          lowercase_filenames: false,
        },
        folder_structure: folderStructure,
        include_associated_docs: false,
        test_mode: testMode,
        test_mode_limit: testModeLimit,
        auto_start: false,
      },
    };

    createJobMutation.mutate(jobData);
  };

  const addFieldMapping = () => {
    setFieldMappings([
      ...fieldMappings,
      { excel_column: '', docuware_field: '' },
    ]);
  };

  const removeFieldMapping = (index: number) => {
    setFieldMappings(fieldMappings.filter((_, i) => i !== index));
  };

  const updateFieldMapping = (
    index: number,
    field: keyof SearchFieldMapping,
    value: string
  ) => {
    const updated = [...fieldMappings];
    updated[index][field] = value;
    setFieldMappings(updated);
  };

  const canProceed = () => {
    switch (activeStep) {
      case 0:
        return excelFile !== null;
      case 1:
        return selectedCabinetId && selectedDialogId;
      case 2:
        return fieldMappings.some((m) => m.excel_column && m.docuware_field);
      case 3:
        return outputDirectory.length > 0;
      default:
        return true;
    }
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        // Paso 1: Subir Excel
        return (
          <Box>
            <Paper
              {...getRootProps()}
              sx={{
                p: 4,
                textAlign: 'center',
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : 'grey.400',
                bgcolor: isDragActive ? 'action.hover' : 'background.paper',
                cursor: 'pointer',
              }}
            >
              <input {...getInputProps()} />
              <UploadIcon
                sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }}
              />
              <Typography variant="h6" gutterBottom>
                {isDragActive
                  ? 'Suelta el archivo aquí'
                  : 'Arrastra un archivo Excel o haz clic para seleccionar'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Formatos soportados: .xlsx, .xls
              </Typography>
            </Paper>

            {excelFile && (
              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  Archivo seleccionado: <strong>{excelFile.name}</strong>
                </Typography>
                <Typography variant="caption">
                  Tamaño: {(excelFile.size / 1024 / 1024).toFixed(2)} MB
                </Typography>
              </Alert>
            )}

            {excelValidation && (
              <Box sx={{ mt: 2 }}>
                <Alert
                  severity={excelValidation.is_valid ? 'success' : 'error'}
                >
                  <Typography variant="body2">
                    {excelValidation.is_valid
                      ? `✓ Excel válido: ${excelValidation.total_rows} filas, ${excelValidation.columns.length} columnas`
                      : 'Excel tiene errores'}
                  </Typography>
                </Alert>
                {excelValidation.columns && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2">
                      Columnas detectadas:
                    </Typography>
                    <Box
                      sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}
                    >
                      {excelValidation.columns.map((col) => (
                        <Chip key={col} label={col} size="small" />
                      ))}
                    </Box>
                  </Box>
                )}
              </Box>
            )}

            {uploadMutation.isPending && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                <CircularProgress />
              </Box>
            )}
          </Box>
        );

      case 1:
        // Paso 2: Seleccionar DocuWare
        return (
          <Box>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>File Cabinet</InputLabel>
              <Select
                value={selectedCabinetId}
                onChange={(e) => setSelectedCabinetId(e.target.value)}
                label="File Cabinet"
              >
                {cabinetsData?.cabinets.map((cabinet) => (
                  <MenuItem key={cabinet.id} value={cabinet.id}>
                    {cabinet.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth disabled={!selectedCabinetId}>
              <InputLabel>Diálogo de Búsqueda</InputLabel>
              <Select
                value={selectedDialogId}
                onChange={(e) => setSelectedDialogId(e.target.value)}
                label="Diálogo de Búsqueda"
              >
                {dialogsData?.dialogs.map((dialog) => (
                  <MenuItem key={dialog.id} value={dialog.id}>
                    {dialog.display_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        );

      case 2:
        // Paso 3: Mapeo de Campos
        return (
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Mapea las columnas del Excel con los campos de DocuWare:
            </Typography>

            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Columna Excel</TableCell>
                  <TableCell>Campo DocuWare</TableCell>
                  <TableCell width={50}></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {fieldMappings.map((mapping, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      <FormControl fullWidth size="small">
                        <Select
                          value={mapping.excel_column || ''}
                          onChange={(e) =>
                            updateFieldMapping(
                              index,
                              'excel_column',
                              e.target.value
                            )
                          }
                          displayEmpty
                        >
                          <MenuItem key="empty-excel" value="">
                            <em>Selecciona una columna</em>
                          </MenuItem>
                          {excelValidation?.columns.map((col) => (
                            <MenuItem key={`excel-${col}`} value={col}>
                              {col}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </TableCell>
                    <TableCell>
                      <FormControl fullWidth size="small">
                        <Select
                          value={mapping.docuware_field || ''}
                          onChange={(e) => {
                            console.log(
                              `Cambiando campo ${index} a:`,
                              e.target.value
                            );
                            updateFieldMapping(
                              index,
                              'docuware_field',
                              e.target.value
                            );
                          }}
                          displayEmpty
                        >
                          <MenuItem key="empty-docuware" value="">
                            <em>Selecciona un campo</em>
                          </MenuItem>
                          {fieldsData?.fields.map((field, fieldIndex) => (
                            <MenuItem
                              key={`docuware-${field.db_name || fieldIndex}`}
                              value={field.db_name || ''}
                            >
                              {field.display_name} ({field.db_name})
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => removeFieldMapping(index)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            <Button
              startIcon={<AddIcon />}
              onClick={addFieldMapping}
              sx={{ mt: 2 }}
            >
              Agregar Campo
            </Button>
          </Box>
        );

      case 3:
        // Paso 4: Configuración
        return (
          <Box>
            <TextField
              fullWidth
              label="Directorio de Salida"
              value={outputDirectory}
              onChange={(e) => setOutputDirectory(e.target.value)}
              sx={{ mb: 2 }}
            />

            <FormControlLabel
              control={
                <Switch
                  checked={tifToPdf}
                  onChange={(e) => setTifToPdf(e.target.checked)}
                />
              }
              label="Convertir TIF a PDF"
            />

            <TextField
              fullWidth
              label="Patrón de Renombrado (opcional)"
              value={renamePattern}
              onChange={(e) => setRenamePattern(e.target.value)}
              helperText="Ejemplo: {Factura}_{Proveedor}"
              sx={{ mb: 2, mt: 2 }}
            />

            <FormControlLabel
              control={
                <Switch
                  checked={testMode}
                  onChange={(e) => setTestMode(e.target.checked)}
                />
              }
              label="Modo Prueba"
            />

            {testMode && (
              <TextField
                type="number"
                label="Límite de registros"
                value={testModeLimit}
                onChange={(e) => setTestModeLimit(parseInt(e.target.value))}
                sx={{ ml: 2 }}
              />
            )}
          </Box>
        );

      case 4:
        // Paso 5: Resumen
        return (
          <Box>
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                Revisa la configuración antes de crear el job
              </Typography>
            </Alert>

            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell>
                    <strong>Archivo Excel</strong>
                  </TableCell>
                  <TableCell>{excelFile?.name}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>
                    <strong>Registros</strong>
                  </TableCell>
                  <TableCell>
                    {testMode ? testModeLimit : excelValidation?.total_rows} de{' '}
                    {excelValidation?.total_rows}
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>
                    <strong>Cabinet</strong>
                  </TableCell>
                  <TableCell>
                    {
                      cabinetsData?.cabinets.find(
                        (c) => c.id === selectedCabinetId
                      )?.name
                    }
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>
                    <strong>Campos Mapeados</strong>
                  </TableCell>
                  <TableCell>
                    {
                      fieldMappings.filter(
                        (m) => m.excel_column && m.docuware_field
                      ).length
                    }
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>
                    <strong>Directorio Salida</strong>
                  </TableCell>
                  <TableCell>{outputDirectory}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Crear Nuevo Job</DialogTitle>
      <DialogContent>
        <Stepper activeStep={activeStep} sx={{ mt: 2, mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {renderStepContent()}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Cancelar</Button>
        <Box sx={{ flex: 1 }} />
        {activeStep > 0 && (
          <Button onClick={handleBack} disabled={uploadMutation.isPending}>
            Atrás
          </Button>
        )}
        {activeStep < steps.length - 1 ? (
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={!canProceed() || uploadMutation.isPending}
          >
            Siguiente
          </Button>
        ) : (
          <Button
            variant="contained"
            onClick={handleCreateJob}
            disabled={createJobMutation.isPending}
          >
            {createJobMutation.isPending ? (
              <CircularProgress size={24} />
            ) : (
              'Crear Job'
            )}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}
