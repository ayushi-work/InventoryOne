"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../../../lib/auth";
import {
  decideBooking,
  fetchAdminBookings,
  formatDate,
  formatMoney,
  type Booking,
} from "../../../lib/api";

const FILTERS = ["all", "pending", "approved", "rejected"];

export default function AdminBookingsPage() {
  const { session, loading } = useAuth();
  const [rows, setRows] = useState<Booking[]>([]);
  const [filter, setFilter] = useState("all");
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
    fetchAdminBookings(session.token, filter === "all" ? undefined : filter)
      .then(setRows)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load bookings."));
  }, [session, filter]);

  async function decide(id: number, action: "approve" | "reject") {
    if (!session) return;
    setBusyId(id);
    setError("");
    setNotice("");
    try {
      const updated = await decideBooking(session.token, id, action);
      setRows((prev) => prev.map((b) => (b.id === id ? updated : b)));
      setNotice(
        action === "approve"
          ? `Booking #${id} approved — plot ${updated.plot_details?.plot_number} marked sold and commission created.`
          : `Booking #${id} rejected — plot ${updated.plot_details?.plot_number} released.`
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Action failed.");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <main className="container">
      <h1 className="page-title">Booking Requests</h1>
      <p className="page-sub">Approve or reject booking requests raised by brokers.</p>

      {notice && <div className="ok">{notice}</div>}
      {error && <div className="error">{error}</div>}

      <div className="legend" style={{ marginBottom: 16 }}>
        {FILTERS.map((f) => (
          <button
            key={f}
            className={`btn small ${filter === f ? "" : "secondary"}`}
            onClick={() => setFilter(f)}
          >
            {f}
          </button>
        ))}
      </div>

      {rows.length === 0 ? (
        <div className="card">No bookings match this filter.</div>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>#</th>
                <th>Broker</th>
                <th>Customer</th>
                <th>Plot</th>
                <th>Token</th>
                <th>Payment</th>
                <th>Status</th>
                <th>Raised</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((b) => (
                <tr key={b.id}>
                  <td>{b.id}</td>
                  <td>{b.broker_name}</td>
                  <td>{b.customer_name}</td>
                  <td>
                    <strong>{b.plot_details?.plot_number}</strong>
                    <div className="muted">{b.plot_details?.size_sq_yds} sq yd</div>
                  </td>
                  <td>{formatMoney(b.token_amount)}</td>
                  <td style={{ textTransform: "capitalize" }}>{b.payment_mode.replace("_", " ")}</td>
                  <td>
                    <span className={`badge ${b.status}`}>{b.status}</span>
                  </td>
                  <td>{formatDate(b.created_at)}</td>
                  <td>
                    {b.status === "pending" ? (
                      <div style={{ display: "flex", gap: 6 }}>
                        <button
                          className="btn success small"
                          disabled={busyId === b.id}
                          onClick={() => decide(b.id, "approve")}
                        >
                          Approve
                        </button>
                        <button
                          className="btn danger small"
                          disabled={busyId === b.id}
                          onClick={() => decide(b.id, "reject")}
                        >
                          Reject
                        </button>
                      </div>
                    ) : (
                      <span className="muted">—</span>
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
