"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useAuth } from "../lib/auth";
import { fetchUnreadCount, markNotificationsRead } from "../lib/api";

export default function NotificationBell() {
  const { session, loading } = useAuth();
  const [unread, setUnread] = useState(0);
  const [open, setOpen] = useState(false);
  const boxRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (loading || !session) return;
    let active = true;

    const load = () => {
      fetchUnreadCount(session.token)
        .then((data) => {
          if (active) setUnread(data.unread);
        })
        .catch(() => undefined);
    };

    load();
    const timer = setInterval(load, 20000);

    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [session, loading]);

  useEffect(() => {
    if (!open) return;
    const onClick = (event: MouseEvent) => {
      if (boxRef.current && !boxRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  async function openPanel() {
    const next = !open;
    setOpen(next);
    if (next && session && unread > 0) {
      await markNotificationsRead(session.token).catch(() => undefined);
      setUnread(0);
    }
  }

  if (loading || !session) return null;

  return (
    <div className="bell-wrap" ref={boxRef}>
      <button
        className="bell"
        onClick={openPanel}
        aria-label={`Notifications${unread ? ` (${unread} unread)` : ""}`}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
        {unread > 0 && <span className="bell-badge">{unread > 9 ? "9+" : unread}</span>}
      </button>

      {open && (
        <div className="bell-panel">
          <div className="bell-panel-head">Notifications</div>
          <Link href="/notifications" onClick={() => setOpen(false)}>
            View all notifications →
          </Link>
        </div>
      )}
    </div>
  );
}
