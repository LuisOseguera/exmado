import { useState } from "react";
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Button,
  Tabs,
  Tab,
} from "@mui/material";
import {
  Add as AddIcon,
  List as ListIcon,
  History as HistoryIcon,
} from "@mui/icons-material";

import JobsList from "../components/JobsList";
import CreateJobWizard from "../components/CreateJobWizard";
import JobDetails from "../components/JobDetails";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [showCreateWizard, setShowCreateWizard] = useState(false);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
    setSelectedJobId(null);
  };

  const handleJobSelect = (jobId: string) => {
    setSelectedJobId(jobId);
  };

  const handleCreateJob = () => {
    setShowCreateWizard(true);
  };

  const handleCloseWizard = () => {
    setShowCreateWizard(false);
  };

  const handleJobCreated = (jobId: string) => {
    setShowCreateWizard(false);
    setSelectedJobId(jobId);
    setActiveTab(1); // Cambiar a tab de jobs activos
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box
        sx={{
          mb: 4,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Box>
          <Typography variant="h3" component="h1" gutterBottom>
            Éxmado
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Sistema de Extracción Masiva de Documentos
          </Typography>
        </Box>
        <Button
          variant="contained"
          size="large"
          startIcon={<AddIcon />}
          onClick={handleCreateJob}
        >
          Nuevo Job
        </Button>
      </Box>

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Left Panel - Lista de Jobs */}
        <Grid item xs={12} md={selectedJobId ? 4 : 12}>
          <Paper sx={{ height: "100%" }}>
            <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
              <Tabs value={activeTab} onChange={handleTabChange}>
                <Tab icon={<ListIcon />} label="Activos" iconPosition="start" />
                <Tab
                  icon={<HistoryIcon />}
                  label="Historial"
                  iconPosition="start"
                />
              </Tabs>
            </Box>

            <TabPanel value={activeTab} index={0}>
              <JobsList
                statusFilter={["pending", "running", "validating", "paused"]}
                onJobSelect={handleJobSelect}
                selectedJobId={selectedJobId}
              />
            </TabPanel>

            <TabPanel value={activeTab} index={1}>
              <JobsList
                statusFilter={[
                  "completed",
                  "completed_with_errors",
                  "failed",
                  "cancelled",
                ]}
                onJobSelect={handleJobSelect}
                selectedJobId={selectedJobId}
              />
            </TabPanel>
          </Paper>
        </Grid>

        {/* Right Panel - Detalles del Job */}
        {selectedJobId && (
          <Grid item xs={12} md={8}>
            <JobDetails
              jobId={selectedJobId}
              onClose={() => setSelectedJobId(null)}
            />
          </Grid>
        )}
      </Grid>

      {/* Wizard de Creación */}
      {showCreateWizard && (
        <CreateJobWizard
          open={showCreateWizard}
          onClose={handleCloseWizard}
          onJobCreated={handleJobCreated}
        />
      )}
    </Container>
  );
}
