/**
 * Hook de React para la Conexión WebSocket (useJobProgress.ts)
 *
 * Un "hook" en React es una función que te permite "engancharte" a las
 * características de React, como el estado y el ciclo de vida, desde un
 * componente de función. Este hook en particular encapsula toda la lógica
 * para manejar una conexión WebSocket que reporta el progreso de un trabajo.
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import type { JobProgressUpdate } from '@/types';

export const useJobProgress = (jobId: string | null) => {
  // --- ESTADO DEL HOOK ---
  // 'progress' guarda el último mensaje de progreso recibido del servidor.
  const [progress, setProgress] = useState<JobProgressUpdate | null>(null);
  // 'isConnected' es una bandera para saber si el WebSocket está activo.
  const [isConnected, setIsConnected] = useState(false);
  // 'ws' es una "referencia" (useRef). A diferencia del estado, no causa
  // que el componente se vuelva a renderizar cuando cambia. La usamos para
  // guardar la instancia del WebSocket a través de los renders.
  const ws = useRef<WebSocket | null>(null);

  // --- FUNCIÓN DE CONEXIÓN ---
  const connect = useCallback(() => {
    // Si no nos pasaste un ID de trabajo, no hacemos nada.
    if (!jobId) return;

    // Determinamos el protocolo (ws o wss para conexiones seguras).
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Construimos la URL correcta para el endpoint del WebSocket.
    const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/jobs/${jobId}`;

    // Si ya existe una conexión, la cerramos antes de abrir una nueva.
    if (ws.current) {
      ws.current.close();
    }

    // Creamos la nueva instancia del WebSocket.
    ws.current = new WebSocket(wsUrl);

    // --- MANEJO DE EVENTOS DEL WEBSOCKET ---
    ws.current.onopen = () => {
      console.log(`[WebSocket] Conexión establecida para el trabajo: ${jobId}`);
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      try {
        const data: JobProgressUpdate = JSON.parse(event.data);
        // Cuando llega un mensaje, actualizamos el estado 'progress'.
        setProgress(data);
      } catch (error) {
        console.error('[WebSocket] Error al procesar el mensaje:', error);
      }
    };

    ws.current.onerror = (error) => {
      console.error('[WebSocket] Ocurrió un error:', error);
    };

    ws.current.onclose = () => {
      console.log(`[WebSocket] Conexión cerrada para el trabajo: ${jobId}`);
      setIsConnected(false);
      // Se eliminó la reconexión automática para que el usuario tenga
      // el control y para evitar bucles de error.
    };
  }, [jobId]); // Esta función se 'recrea' solo si el jobId cambia.

  // --- FUNCIÓN DE DESCONEXIÓN ---
  const disconnect = useCallback(() => {
    if (ws.current) {
      // Le quitamos el manejador 'onclose' antes de cerrar para evitar que
      // se ejecute lógica de reconexión no deseada.
      ws.current.onclose = null;
      ws.current.close();
      ws.current = null;
    }
  }, []);

  // --- EFECTO DE CICLO DE VIDA ---
  // `useEffect` es el hook que nos permite ejecutar código cuando el
  // componente se "monta", se "actualiza" o se "desmonta".
  useEffect(() => {
    // Si nos pasaron un `jobId`, iniciamos la conexión.
    if (jobId) {
      connect();
    }

    // La función que retornamos en un useEffect es la "función de limpieza".
    // Se ejecuta cuando el componente se desmonta (por ejemplo, si el usuario
    // navega a otra página). Es el lugar perfecto para cerrar conexiones.
    return () => {
      disconnect();
    };
  }, [jobId, connect, disconnect]); // Este efecto se ejecuta de nuevo si alguna de estas dependencias cambia.

  // --- VALORES RETORNADOS ---
  // El hook expone el estado y las funciones que los componentes pueden necesitar.
  return {
    progress,
    isConnected,
  };
};
