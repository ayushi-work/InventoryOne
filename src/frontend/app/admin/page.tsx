"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuth } from "../../lib/auth";
import { fetchAdminStats, type AdminStats } from "../../lib/api";

export default function AdminDashboard() {
  const { session, loading } = useAuth();
  const [stats, setStats] = useState<AdminStats | null>(null);
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
    fetchAdminStats(session.token)
      .then(setStats)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load stats."));
  }, [session, loading]);

  const tiles: Array<[string, number | undefined, string]> = stats
    ? [
        ["Brokers", stats.brokers, "#1f3864"],
        ["KYC pending", stats.kyc_pending, "#f29e1b"],
        ["Projects", stats.projects, "#1f3864"],
        ["Plots", stats.plots, "#1f3864"],
        ["Available", stats.available_plots, "#2e7d32"],
        ["On hold", stats.on_hold_plots, "#f29e1b"],
        ["Sold", stats.sold_plots, "#c0392b"],
        ["Pending bookings", stats.pending_bookings, "#f29e1b"],
        ["Approved bookings", stats.approved_bookings, "#2e7d32"],
        ["Commissions", stats.commissions, "#2e9e8f"],
        ["Unreleased", stats.unreleased_commissions, "#c0392b"],
      ]
    : [];

  return (
    <main className="container">
      <h1 className="page-title">Company Dashboard</h1>
      <p className="page-sub">
        Overview of brokers, inventory, booking requests and commissions across the platform.
      </p>

      {error && <div className="error">{error}</div>}

      <div className="stats">
        {tiles.map(([label, value, color]) => (
          <div className="stat" key={label} style={{ borderLeftColor: color }}>
            <div className="v">{value ?? "—"}</div>
            <div className="k">{label}</div>
          </div>
        ))}
      </div>

      <div className="card-grid">
        <Link href="/admin/bookings">
          <div className="card">
            <h3>Booking requests</h3>
            <p className="muted">
              Review pending booking requests and approve or reject them. Approving a booking
              marks the plot as sold and creates the broker commission.
            </p>
            <span className="btn small">Open bookings →</span>
          </div>
        </Link>
        <Link href="/admin/commissions">
          <div className="card">
            <h3>Commission management</h3>
            <p className="muted">
              Review commission ledger with TDS deduction and release payments to brokers.
            </p>
            <span className="btn small">Open commissions →</span>
          </div>
        </Link>
        <Link href="/projects">
          <div className="card">
            <h3>Project inventory</h3>
            <p className="muted">
              Browse active projects and live plot availability across every layout.
            </p>
            <span className="btn small">Open projects →</span>
          </div>
        </Link>
      </div>
    </main>
  );
}
