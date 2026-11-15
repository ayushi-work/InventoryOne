"use client";

import { useEffect, useRef, useState } from "react";

const WS_BASE = (process.env.NEXT_PUBLIC_WS_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000"
)
  .replace(/^http/, "ws")
  .replace(/\/$/, "");

export type InventoryEvent = {
  type: string;
  project_id?: number | null;
  plot_id?: number | null;
  status?: string;
  counts?: Record<string, number>;
};

/**
 * Subscribes to live plot-availability updates over a WebSocket.
 *
 * Falls back to polling when the socket cannot be opened, so the dashboard
 * keeps working even without Redis or a running Channels worker.
 */
export function useLiveInventory(onEvent: (event: InventoryEvent) => void) {
  const [connected, setConnected] = useState(false);
  const handler = useRef(onEvent);
  handler.current = onEvent;

  useEffect(() => {
    let socket: WebSocket | null = null;
    let pollTimer: ReturnType<typeof setInterval> | null = null;
    let cancelled = false;

    const startPolling = () => {
      if (pollTimer || cancelled) return;
      pollTimer = setInterval(() => {
        handler.current({ type: "poll" });
      }, 15000);
    };

    try {
      socket = new WebSocket(`${WS_BASE}/ws/inventory/`);
    } catch {
      socket = null;
    }

    if (!socket) {
      startPolling();
      return () => {
        cancelled = true;
        if (pollTimer) clearInterval(pollTimer);
      };
    }

    socket.onopen = () => {
      if (cancelled) return;
      setConnected(true);
    };

    socket.onmessage = (message) => {
      try {
        const payload = JSON.parse(message.data) as InventoryEvent;
        if (payload.type === "inventory") handler.current(payload);
      } catch {
        // ignore malformed frames
      }
    };

    socket.onerror = () => {
      setConnected(false);
    };

    socket.onclose = () => {
      setConnected(false);
      startPolling();
    };

    // If the socket does not open quickly, fall back to polling anyway.
    const handshakeTimer = setTimeout(() => {
      if (!connected && socket && socket.readyState !== WebSocket.OPEN) {
        startPolling();
      }
    }, 4000);

    return () => {
      cancelled = true;
      clearTimeout(handshakeTimer);
      if (pollTimer) clearInterval(pollTimer);
      if (socket && socket.readyState <= WebSocket.OPEN) socket.close();
    };
  }, []);

  return { connected };
}
