"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuth } from "../../lib/auth";
import {
  fetchBookings,
  formatDate,
  formatMoney,
  generateDemandLetter,
  type Booking,
} from "../../lib/api";

export default function BookingsPage() {
  const { session, loading } = useAuth();
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState<number | null>(null);
  const [state, setState] = useState<"loading" | "ready">("loading");

  useEffect(() => {
    if (loading) return;
    if (!session) {
      window.location.href = "/";
      return;
    }
    fetchBookings(session.token)
      .then((d) => {
        setBookings(d);
        setState("ready");
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load bookings."));
  }, [session, loading]);

  if (state === "loading") return <div className="loading">Loading bookings…</div>;

  async function downloadDemandLetter(booking: Booking) {
    if (!session) return;
    setError("");
    setNotice("");
    setBusy(booking.id);
    try {
      const doc = await generateDemandLetter(session.token, booking.id);
      setNotice(`Demand letter generated for plot ${booking.plot_details?.plot_number}.`);
      window.open(doc.download_url, "_blank");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not generate the demand letter.");
    } finally {
      setBusy(null);
    }
  }

  return (
    <main className="container">
      <h1 className="page-title">My Bookings</h1>
      <p className="page-sub">Track every booking request raised by you and its approval status.</p>

      {notice && <div className="ok">{notice}</div>}
      {error && <div className="error">{error}</div>}

      {bookings.length === 0 && (
        <div className="card">
          No bookings yet. <Link href="/projects">Browse projects</Link> to raise one.
        </div>
      )}

      {bookings.length > 0 && (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>#</th>
                <th>Plot</th>
                <th>Customer</th>
                <th>Token amount</th>
                <th>Payment</th>
                <th>Status</th>
                <th>Commission</th>
                <th>Raised on</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {bookings.map((b) => (
                <tr key={b.id}>
                  <td>{b.id}</td>
                  <td>
                    <strong>{b.plot_details?.plot_number}</strong>
                    <div className="muted">{b.plot_details?.size_sq_yds} sq yd</div>
                  </td>
                  <td>{b.customer_name}</td>
                  <td>{formatMoney(b.token_amount)}</td>
                  <td style={{ textTransform: "capitalize" }}>{b.payment_mode.replace("_", " ")}</td>
                  <td>
                    <span className={`badge ${b.status}`}>{b.status}</span>
                  </td>
                  <td>{b.commission ? formatMoney(b.commission) : "—"}</td>
                  <td>{formatDate(b.created_at)}</td>
                  <td>
                    {b.status === "approved" && (
                      <button
                        className="btn small"
                        disabled={busy === b.id}
                        onClick={() => void downloadDemandLetter(b)}
                      >
                        {busy === b.id ? "Generating…" : "Demand letter"}
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
