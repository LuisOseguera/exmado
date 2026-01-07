import { useEffect, useRef, useState, useCallback } from 'react';
import type { JobProgressUpdate } from '@/types';

export const useJobProgress = (jobId: string | null) => {
  const [progress, setProgress] = useState<JobProgressUpdate | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (!jobId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/jobs/${jobId}`;

    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('WebSocket conectado');
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      try {
        const data: JobProgressUpdate = JSON.parse(event.data);
        setProgress(data);
      } catch (error) {
        console.error('Error al parsear mensaje WebSocket:', error);
      }
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.current.onclose = () => {
      console.log('WebSocket desconectado');
      setIsConnected(false);

      // Reconectar después de 3 segundos
      setTimeout(() => {
        if (jobId) {
          connect();
        }
      }, 3000);
    };
  }, [jobId]);

  const disconnect = useCallback(() => {
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
  }, []);

  const sendMessage = useCallback((message: { [key: string]: unknown }) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  }, []);

  const requestStatus = useCallback(() => {
    sendMessage({ type: 'get_status' });
  }, [sendMessage]);

  useEffect(() => {
    if (jobId) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [jobId, connect, disconnect]);

  return {
    progress,
    isConnected,
    requestStatus,
    disconnect,
  };
};
