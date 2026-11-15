"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../../../lib/auth";
import { fetchAuditLog, formatDate, type AuditEntry } from "../../../lib/api";

export default function AdminAuditPage() {
  const { session, loading } = useAuth();
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [error, setError] = useState("");

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
    fetchAuditLog(session.token)
      .then(setEntries)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load the audit log."));
  }, [session, loading]);

  return (
    <main className="container">
      <h1 className="page-title">Audit Trail</h1>
      <p className="page-sub">
        Every booking approval, commission release and inventory change is recorded here.
      </p>

      {error && <div className="error">{error}</div>}

      {entries.length === 0 ? (
        <div className="card">No audit entries yet.</div>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>When</th>
                <th>Actor</th>
                <th>Action</th>
                <th>Entity</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((e) => (
                <tr key={e.id}>
                  <td>{formatDate(e.created_at)}</td>
                  <td>{e.actor_name || "system"}</td>
                  <td>
                    <span className="badge neutral">{e.action}</span>
                  </td>
                  <td>
                    {e.entity_type} {e.entity_id ? `#${e.entity_id}` : ""}
                  </td>
                  <td className="muted">
                    {Object.keys(e.details ?? {}).length
                      ? Object.entries(e.details)
                          .map(([k, v]) => `${k}: ${String(v)}`)
                          .join(", ")
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
