/**
 * Componente Principal de la Aplicación (App.tsx)
 *
 * Este es el punto de entrada de tu aplicación de React. Aquí es donde vos
 * configurás todos los "proveedores" de contexto globales que le dan
 * funcionalidades a todos los componentes hijos.
 *
 * - QueryClientProvider: Para el manejo de datos con TanStack Query.
 * - ThemeProvider: Para aplicar el tema de Material-UI.
 * - SnackbarProvider: Para mostrar notificaciones en toda la app.
 * - Router: Para manejar la navegación y las rutas.
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, createTheme, CssBaseline, Box, Grid, Typography } from '@mui/material';
import { SnackbarProvider } from 'notistack';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { SnackbarUtilsConfigurator } from './utils/snackbar';
import JobsList from '@/components/JobsList';
import JobDetails from '@/components/JobDetails';
import { useState } from 'react';

// Configuramos el cliente de React Query. Esta es la herramienta que nos ayuda
// a manejar los datos de la API, incluyendo el cache, las recargas automáticas, etc.
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false, // No queremos que recargue los datos solo por cambiar de ventana.
      retry: 1, // Si una petición falla, que la intente una vez más.
      staleTime: 5000, // Considera los datos "frescos" por 5 segundos.
    },
  },
});

// Definimos un tema básico para Material-UI, para que la aplicación tenga un
// aspecto visual coherente.
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
  },
  typography: {
    fontFamily: ['-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'].join(','),
  },
});

// Creamos un componente simple para el layout principal de la página.
const MainLayout = () => {
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

  return (
    <Box sx={{ display: 'flex', height: '100vh', p: 2, gap: 2, backgroundColor: '#f4f6f8' }}>
      <Grid container spacing={2}>
        <Grid item xs={12} md={4} lg={3}>
            <Typography variant="h5" gutterBottom>
                Éxmado
            </Typography>
            <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                Sistema de Extracción Masiva de Documentos
            </Typography>
          <JobsList onJobSelect={setSelectedJobId} selectedJobId={selectedJobId} />
        </Grid>
        <Grid item xs={12} md={8} lg={9}>
          <JobDetails jobId={selectedJobId} />
        </Grid>
      </Grid>
    </Box>
  );
};

function App() {
  return (
    // Proveedor de React Query
    <QueryClientProvider client={queryClient}>
      {/* Proveedor de Tema de Material-UI */}
      <ThemeProvider theme={theme}>
        <CssBaseline /> {/* Normaliza los estilos CSS entre navegadores */}
        {/* Proveedor para las notificaciones (snackbars) */}
        <SnackbarProvider maxSnack={3} anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
          <SnackbarUtilsConfigurator />
          {/* Proveedor de Rutas */}
          <Router>
            <Routes>
              {/* La única ruta de nuestra aplicación que renderiza el layout principal */}
              <Route path="/" element={<MainLayout />} />
            </Routes>
          </Router>
        </SnackbarProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
