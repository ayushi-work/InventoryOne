"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../../lib/auth";
import {
  createTicket,
  fetchCompanyProfile,
  fetchTickets,
  formatDate,
  type CompanyProfile,
  type SupportTicket,
} from "../../lib/api";

const STATUS_CLASS: Record<string, string> = {
  open: "on_hold",
  in_progress: "pending",
  resolved: "available",
};

export default function SupportPage() {
  const { session, loading } = useAuth();
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [company, setCompany] = useState<CompanyProfile | null>(null);
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [priority, setPriority] = useState("normal");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (loading) return;
    if (!session) {
      window.location.href = "/";
      return;
    }
    fetchTickets(session.token)
      .then(setTickets)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load tickets."));
    fetchCompanyProfile(session.token)
      .then(setCompany)
      .catch(() => undefined);
  }, [session, loading]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!session) return;
    setError("");
    setNotice("");
    setBusy(true);
    try {
      const created = await createTicket(session.token, { subject, message, priority });
      setTickets((prev) => [created, ...prev]);
      setSubject("");
      setMessage("");
      setNotice(`Ticket #${created.id} raised. Our team will respond shortly.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not raise the ticket.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="container">
      <h1 className="page-title">Support</h1>
      <p className="page-sub">
        Raise a ticket for anything you need help with, or reach your relationship manager
        directly.
      </p>

      {notice && <div className="ok">{notice}</div>}
      {error && <div className="error">{error}</div>}

      {company && (
        <div className="card" style={{ marginBottom: 18 }}>
          <h3>Your relationship manager</h3>
          <div className="kv">
            <span className="k">Name</span>
            <span className="v">{company.rm_name}</span>
          </div>
          <div className="kv">
            <span className="k">Phone</span>
            <span className="v">{company.rm_phone}</span>
          </div>
          <div className="kv">
            <span className="k">Email</span>
            <span className="v">{company.rm_email}</span>
          </div>
          <div className="kv">
            <span className="k">Support desk</span>
            <span className="v">
              {company.support_email} · {company.support_phone}
            </span>
          </div>
        </div>
      )}

      <div className="row" style={{ alignItems: "flex-start" }}>
        <div className="card" style={{ flex: "0 0 340px" }}>
          <h3>Raise a ticket</h3>
          <form onSubmit={submit}>
            <div className="field">
              <label htmlFor="subject">Subject *</label>
              <input
                id="subject"
                required
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Payment link for booking"
              />
            </div>
            <div className="field">
              <label htmlFor="priority">Priority</label>
              <select id="priority" value={priority} onChange={(e) => setPriority(e.target.value)}>
                <option value="low">Low</option>
                <option value="normal">Normal</option>
                <option value="high">High</option>
              </select>
            </div>
            <div className="field">
              <label htmlFor="message">Message *</label>
              <textarea
                id="message"
                required
                rows={4}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Describe the issue…"
              />
            </div>
            <button className="btn" type="submit" disabled={busy} style={{ width: "100%" }}>
              {busy ? "Submitting…" : "Raise ticket"}
            </button>
          </form>
        </div>

        <div style={{ flex: 1, minWidth: 320 }}>
          <h2 className="section-title" style={{ marginTop: 0 }}>
            My tickets
          </h2>
          {tickets.length === 0 ? (
            <div className="card">No tickets raised yet.</div>
          ) : (
            <div style={{ display: "grid", gap: 12 }}>
              {tickets.map((t) => (
                <div className="card" key={t.id}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 10,
                      marginBottom: 6,
                    }}
                  >
                    <strong style={{ color: "var(--navy)" }}>#{t.id} {t.subject}</strong>
                    <span className={`badge ${STATUS_CLASS[t.status] ?? "neutral"}`}>
                      {t.status.replace("_", " ")}
                    </span>
                    <span className="badge neutral">{t.priority}</span>
                    <span className="muted" style={{ marginLeft: "auto" }}>
                      {formatDate(t.created_at)}
                    </span>
                  </div>
                  <p className="muted" style={{ margin: "0 0 6px" }}>
                    {t.message}
                  </p>
                  {t.response && (
                    <div className="hint" style={{ marginBottom: 0 }}>
                      <strong>Response:</strong> {t.response}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
