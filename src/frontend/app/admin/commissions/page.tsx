"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../../../lib/auth";
import {
  fetchAdminBookings,
  fetchAdminCommissions,
  releaseCommission,
  formatDate,
  formatMoney,
  type Booking,
  type Commission,
} from "../../../lib/api";

export default function AdminCommissionsPage() {
  const { session, loading } = useAuth();
  const [approved, setApproved] = useState<Booking[]>([]);
  const [commissions, setCommissions] = useState<Commission[]>([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busyId, setBusyId] = useState<number | null>(null);

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
    fetchAdminBookings(session.token, "approved")
      .then(setApproved)
      .catch(() => undefined);
  }, [session]);

  async function loadCommissions() {
    if (!session) return;
    try {
      const data = await fetchAdminCommissions(session.token);
      setCommissions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load commissions.");
    }
  }

  useEffect(() => {
    void loadCommissions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session]);

  async function release(id: number) {
    if (!session) return;
    setBusyId(id);
    setError("");
    setNotice("");
    try {
      await releaseCommission(session.token, id);
      await loadCommissions();
      setNotice(`Commission #${id} released to the broker.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Release failed.");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <main className="container">
      <h1 className="page-title">Commission Management</h1>
      <p className="page-sub">
        Commissions are generated automatically when a booking is approved. Release them to pay the
        broker.
      </p>

      {notice && <div className="ok">{notice}</div>}
      {error && <div className="error">{error}</div>}

      <h2 className="section-title">Approved bookings</h2>
      {approved.length === 0 ? (
        <div className="card">No approved bookings yet.</div>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>#</th>
                <th>Broker</th>
                <th>Customer</th>
                <th>Plot</th>
                <th>Token amount</th>
                <th>Commission %</th>
                <th>Decided on</th>
              </tr>
            </thead>
            <tbody>
              {approved.map((b) => (
                <tr key={b.id}>
                  <td>{b.id}</td>
                  <td>{b.broker_name}</td>
                  <td>{b.customer_name}</td>
                  <td>{b.plot_details?.plot_number}</td>
                  <td>{formatMoney(b.token_amount)}</td>
                  <td>{b.commission_pct}%</td>
                  <td>{formatDate(b.decided_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <h2 className="section-title">Commission ledger</h2>
      {commissions.length === 0 ? (
        <div className="card">No commissions generated yet.</div>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Plot</th>
                <th>Broker</th>
                <th>Customer</th>
                <th>Gross</th>
                <th>TDS</th>
                <th>Net</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {commissions.map((c) => (
                <tr key={c.id}>
                  <td>
                    <strong>{c.plot_label}</strong>
                    <div className="muted">{c.project_name}</div>
                  </td>
                  <td>{c.broker_name}</td>
                  <td>{c.customer_name}</td>
                  <td>{formatMoney(c.amount)}</td>
                  <td style={{ color: "#c0392b" }}>− {formatMoney(c.tds_amount)}</td>
                  <td>
                    <strong style={{ color: "#2e7d32" }}>{formatMoney(c.net_amount)}</strong>
                  </td>
                  <td>
                    <span className={`badge ${c.released ? "approved" : "pending"}`}>
                      {c.released ? "released" : "unreleased"}
                    </span>
                  </td>
                  <td>
                    {c.released ? (
                      <span className="muted">{formatDate(c.released_at)}</span>
                    ) : (
                      <button
                        className="btn success small"
                        disabled={busyId === c.id}
                        onClick={() => release(c.id)}
                      >
                        Release
                      </button>
                    )}
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
