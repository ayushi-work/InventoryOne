"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../../../lib/auth";
import {
  fetchAdminTickets,
  formatDate,
  updateAdminTicket,
  type SupportTicket,
} from "../../../lib/api";

const STATUS_CLASS: Record<string, string> = {
  open: "on_hold",
  in_progress: "pending",
  resolved: "available",
};

export default function AdminTicketsPage() {
  const { session, loading } = useAuth();
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [filter, setFilter] = useState("all");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [drafts, setDrafts] = useState<Record<number, string>>({});

  useEffect(() => {
    if (loading) return;
    if (!session) {
      window.location.href = "/";
      return;
    }
    if (session.role !== "admin") {
      window.location.href = "/projects";
      return;
    }
  }, [session, loading]);

  useEffect(() => {
    if (!session || session.role !== "admin") return;
    fetchAdminTickets(session.token, filter === "all" ? undefined : filter)
      .then(setTickets)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load tickets."));
  }, [session, filter]);

  async function resolve(ticket: SupportTicket, status: string) {
    if (!session) return;
    setError("");
    setNotice("");
    try {
      const updated = await updateAdminTicket(session.token, {
        id: ticket.id,
        status,
        response: drafts[ticket.id] ?? ticket.response,
      });
      setTickets((prev) => prev.map((t) => (t.id === ticket.id ? updated : t)));
      setNotice(`Ticket #${ticket.id} marked ${status.replace("_", " ")}.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update the ticket.");
    }
  }

  return (
    <main className="container">
      <h1 className="page-title">Support Tickets</h1>
      <p className="page-sub">Respond to broker support requests and close them off.</p>

      {notice && <div className="ok">{notice}</div>}
      {error && <div className="error">{error}</div>}

      <div className="legend" style={{ marginBottom: 16 }}>
        {["all", "open", "in_progress", "resolved"].map((f) => (
          <button
            key={f}
            className={`btn small ${filter === f ? "" : "secondary"}`}
            onClick={() => setFilter(f)}
          >
            {f.replace("_", " ")}
          </button>
        ))}
      </div>

      {tickets.length === 0 ? (
        <div className="card">No tickets match this filter.</div>
      ) : (
        <div style={{ display: "grid", gap: 12 }}>
          {tickets.map((t) => (
            <div className="card" key={t.id}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                <strong style={{ color: "var(--navy)" }}>
                  #{t.id} {t.subject}
                </strong>
                <span className={`badge ${STATUS_CLASS[t.status] ?? "neutral"}`}>
                  {t.status.replace("_", " ")}
                </span>
                <span className="badge neutral">{t.priority}</span>
                <span className="muted" style={{ marginLeft: "auto" }}>
                  {t.broker_name} · {formatDate(t.created_at)}
                </span>
              </div>
              <p className="muted" style={{ margin: "0 0 10px" }}>{t.message}</p>

              <div className="field" style={{ marginBottom: 8 }}>
                <label>Response</label>
                <textarea
                  rows={2}
                  value={drafts[t.id] ?? t.response}
                  onChange={(e) => setDrafts({ ...drafts, [t.id]: e.target.value })}
                  placeholder="Write a reply to the broker…"
                />
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <button className="btn small" onClick={() => void resolve(t, "in_progress")}>
                  Mark in progress
                </button>
                <button className="btn success small" onClick={() => void resolve(t, "resolved")}>
                  Resolve
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
