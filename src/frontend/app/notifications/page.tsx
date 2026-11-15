"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuth } from "../../lib/auth";
import { fetchNotifications, markNotificationsRead, type Notification } from "../../lib/api";

const KIND_CLASS: Record<string, string> = {
  project: "blue",
  scheme: "amber",
  booking: "green",
  commission: "green",
  system: "gray",
};

export default function NotificationsPage() {
  const { session, loading } = useAuth();
  const [items, setItems] = useState<Notification[]>([]);
  const [filter, setFilter] = useState<"all" | "unread">("all");
  const [error, setError] = useState("");
  const [state, setState] = useState<"loading" | "ready">("loading");

  useEffect(() => {
    if (loading) return;
    if (!session) {
      window.location.href = "/";
      return;
    }
    fetchNotifications(session.token, filter === "unread")
      .then((data) => {
        setItems(data);
        setState("ready");
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Could not load notifications.");
        setState("ready");
      });
  }, [session, loading, filter]);

  async function markAllRead() {
    if (!session) return;
    await markNotificationsRead(session.token).catch(() => undefined);
    setItems((prev) => prev.map((n) => ({ ...n, read: true })));
  }

  if (state === "loading") return <div className="loading">Loading notifications…</div>;

  const unread = items.filter((n) => !n.read).length;

  return (
    <main className="container">
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div>
          <h1 className="page-title">Notifications</h1>
          <p className="page-sub">
            New projects, schemes and booking updates from the company.
          </p>
        </div>
        {unread > 0 && (
          <button className="btn secondary small" style={{ marginLeft: "auto" }} onClick={markAllRead}>
            Mark all read
          </button>
        )}
      </div>

      {error && <div className="error">{error}</div>}

      <div className="legend" style={{ marginBottom: 16 }}>
        <button
          className={`btn small ${filter === "all" ? "" : "secondary"}`}
          onClick={() => setFilter("all")}
        >
          All
        </button>
        <button
          className={`btn small ${filter === "unread" ? "" : "secondary"}`}
          onClick={() => setFilter("unread")}
        >
          Unread
        </button>
      </div>

      {items.length === 0 ? (
        <div className="card">
          {filter === "unread" ? "No unread notifications." : "No notifications yet."}
        </div>
      ) : (
        <div className="notif-list">
          {items.map((n) => (
            <div className={`notif ${n.read ? "" : "unread"}`} key={n.id}>
              <span className={`notif-dot ${KIND_CLASS[n.kind] ?? "gray"}`} />
              <div className="notif-body">
                <div className="notif-title">
                  {n.title}
                  <span className="notif-kind">{n.kind_display}</span>
                </div>
                {n.body && <p className="notif-text">{n.body}</p>}
                <span className="notif-time">
                  {new Date(n.created_at).toLocaleString("en-IN", {
                    day: "2-digit",
                    month: "short",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </div>
              {n.link && (
                <Link className="btn secondary small" href={n.link}>
                  Open
                </Link>
              )}
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
