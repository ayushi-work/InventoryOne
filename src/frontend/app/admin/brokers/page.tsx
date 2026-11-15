"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../../../lib/auth";
import {
  broadcastNotification,
  fetchAdminBrokers,
  formatDate,
  updateBrokerKyc,
  type Broker,
} from "../../../lib/api";

export default function AdminBrokersPage() {
  const { session, loading } = useAuth();
  const [brokers, setBrokers] = useState<Broker[]>([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [kind, setKind] = useState("scheme");
  const [busy, setBusy] = useState(false);

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
    fetchAdminBrokers(session.token)
      .then(setBrokers)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load brokers."));
  }, [session, loading]);

  async function setKyc(broker: Broker, kyc_status: string) {
    if (!session) return;
    try {
      const updated = await updateBrokerKyc(session.token, broker.id, kyc_status);
      setBrokers((prev) => prev.map((b) => (b.id === broker.id ? updated : b)));
      setNotice(`${updated.email} KYC marked ${kyc_status}.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update KYC.");
    }
  }

  async function broadcast(e: React.FormEvent) {
    e.preventDefault();
    if (!session) return;
    setError("");
    setNotice("");
    setBusy(true);
    try {
      const res = await broadcastNotification(session.token, { title, body, kind });
      setTitle("");
      setBody("");
      setNotice(`Notification sent to ${res.sent} brokers.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not send the notification.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="container">
      <h1 className="page-title">Brokers & KYC</h1>
      <p className="page-sub">Verify broker KYC and broadcast announcements to all brokers.</p>

      {notice && <div className="ok">{notice}</div>}
      {error && <div className="error">{error}</div>}

      <div className="row" style={{ alignItems: "flex-start" }}>
        <div className="card" style={{ flex: "0 0 340px" }}>
          <h3>Broadcast a notification</h3>
          <form onSubmit={broadcast}>
            <div className="field">
              <label htmlFor="btitle">Title *</label>
              <input id="btitle" required value={title}
                     onChange={(e) => setTitle(e.target.value)}
                     placeholder="Festive scheme live" />
            </div>
            <div className="field">
              <label htmlFor="bkind">Type</label>
              <select id="bkind" value={kind} onChange={(e) => setKind(e.target.value)}>
                <option value="project">New project</option>
                <option value="scheme">Scheme</option>
                <option value="system">System</option>
              </select>
            </div>
            <div className="field">
              <label htmlFor="bbody">Message</label>
              <textarea id="bbody" rows={3} value={body}
                        onChange={(e) => setBody(e.target.value)} />
            </div>
            <button className="btn" type="submit" disabled={busy} style={{ width: "100%" }}>
              {busy ? "Sending…" : "Send to all brokers"}
            </button>
          </form>
        </div>

        <div style={{ flex: 1, minWidth: 340 }}>
          <h2 className="section-title" style={{ marginTop: 0 }}>
            Registered brokers
          </h2>
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Broker</th>
                  <th>PAN</th>
                  <th>RERA</th>
                  <th>KYC status</th>
                  <th>Joined</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {brokers.map((b) => (
                  <tr key={b.id}>
                    <td>
                      <strong>{b.name || b.email}</strong>
                      <div className="muted">{b.email}</div>
                    </td>
                    <td>{b.pan_number || "—"}</td>
                    <td>{b.rera_number || "—"}</td>
                    <td>
                      <span className={`badge ${b.kyc_status === "approved" ? "available" : b.kyc_status === "rejected" ? "sold" : "on_hold"}`}>
                        {b.kyc_status}
                      </span>
                    </td>
                    <td>{formatDate(b.created_at)}</td>
                    <td>
                      {b.kyc_status !== "approved" ? (
                        <button className="btn success small" onClick={() => void setKyc(b, "approved")}>
                          Approve
                        </button>
                      ) : (
                        <button className="btn danger small" onClick={() => void setKyc(b, "rejected")}>
                          Reject
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  );
}
