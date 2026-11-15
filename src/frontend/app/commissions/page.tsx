"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../../lib/auth";
import { fetchCommissions, formatDate, formatMoney, type Commission } from "../../lib/api";

export default function CommissionsPage() {
  const { session, loading } = useAuth();
  const [rows, setRows] = useState<Commission[]>([]);
  const [error, setError] = useState("");
  const [state, setState] = useState<"loading" | "ready">("loading");

  useEffect(() => {
    if (loading) return;
    if (!session) {
      window.location.href = "/";
      return;
    }
    fetchCommissions(session.token)
      .then((d) => {
        setRows(d);
        setState("ready");
      })
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Failed to load commissions.")
      );
  }, [session, loading]);

  if (state === "loading") return <div className="loading">Loading commissions…</div>;

  const gross = rows.reduce((s, r) => s + parseFloat(r.amount), 0);
  const tds = rows.reduce((s, r) => s + parseFloat(r.tds_amount), 0);
  const net = rows.reduce((s, r) => s + parseFloat(r.net_amount), 0);
  const released = rows.filter((r) => r.released).length;

  return (
    <main className="container">
      <h1 className="page-title">Commissions</h1>
      <p className="page-sub">
        Commission earned on approved bookings, with TDS deduction and release status.
      </p>

      {error && <div className="error">{error}</div>}

      <div className="stats">
        <div className="stat">
          <div className="v">{formatMoney(gross)}</div>
          <div className="k">Gross commission</div>
        </div>
        <div className="stat" style={{ borderLeftColor: "#c0392b" }}>
          <div className="v">{formatMoney(tds)}</div>
          <div className="k">TDS deducted</div>
        </div>
        <div className="stat" style={{ borderLeftColor: "#2e7d32" }}>
          <div className="v">{formatMoney(net)}</div>
          <div className="k">Net payable</div>
        </div>
        <div className="stat" style={{ borderLeftColor: "#f29e1b" }}>
          <div className="v">
            {released}/{rows.length}
          </div>
          <div className="k">Released</div>
        </div>
      </div>

      {rows.length === 0 ? (
        <div className="card">
          No commissions yet. Commissions are created when the company approves a booking.
        </div>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Plot</th>
                <th>Project</th>
                <th>Customer</th>
                <th>Commission</th>
                <th>TDS</th>
                <th>Net</th>
                <th>Status</th>
                <th>Released on</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((c) => (
                <tr key={c.id}>
                  <td>
                    <strong>{c.plot_label}</strong>
                  </td>
                  <td>{c.project_name}</td>
                  <td>{c.customer_name}</td>
                  <td>{formatMoney(c.amount)}</td>
                  <td style={{ color: "#c0392b" }}>
                    − {formatMoney(c.tds_amount)} ({c.tds_pct}%)
                  </td>
                  <td>
                    <strong style={{ color: "#2e7d32" }}>{formatMoney(c.net_amount)}</strong>
                  </td>
                  <td>
                    <span className={`badge ${c.released ? "approved" : "pending"}`}>
                      {c.released ? "released" : "unreleased"}
                    </span>
                  </td>
                  <td>{formatDate(c.released_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
