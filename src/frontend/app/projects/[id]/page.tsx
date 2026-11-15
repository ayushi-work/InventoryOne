"use client";

import { Suspense } from "react";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuth } from "../../../lib/auth";
import {
  createBooking,
  createCustomer,
  fetchCustomers,
  fetchProject,
  formatMoney,
  type Customer,
  type Plot,
  type Project,
} from "../../../lib/api";

export default function ProjectDetailPage() {
  return (
    <Suspense
      fallback={
        <main className="container">
          <div className="loading">Loading project…</div>
        </main>
      }
    >
      <ProjectDetail />
    </Suspense>
  );
}

function ProjectDetail() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { session, loading } = useAuth();

  const [project, setProject] = useState<Project | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selected, setSelected] = useState<Plot | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);

  // booking form state
  const [customerId, setCustomerId] = useState("");
  const [newName, setNewName] = useState("");
  const [newPhone, setNewPhone] = useState("");
  const [tokenAmount, setTokenAmount] = useState("");
  const [paymentMode, setPaymentMode] = useState("upi");
  const [useNewCustomer, setUseNewCustomer] = useState(false);

  useEffect(() => {
    if (loading) return;
    if (!session) {
      window.location.href = "/";
      return;
    }
    const id = params?.id;
    if (!id) return;
    Promise.all([fetchProject(session.token, id), fetchCustomers(session.token)])
      .then(([proj, custs]) => {
        setProject(proj);
        setCustomers(custs);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load project."));
  }, [session, loading, params?.id]);

  async function submitBooking(e: React.FormEvent) {
    e.preventDefault();
    if (!session || !selected) return;
    setError("");
    setNotice("");
    setBusy(true);
    try {
      let targetCustomerId = Number(customerId);
      if (useNewCustomer) {
        const created = await createCustomer(session.token, {
          name: newName,
          phone: newPhone,
        });
        targetCustomerId = created.id;
        setCustomers((prev) => [created, ...prev]);
      }
      if (!targetCustomerId) throw new Error("Select or create a customer first.");

      await createBooking(session.token, {
        customer: targetCustomerId,
        plot: selected.id,
        token_amount: Number(tokenAmount),
        payment_mode: paymentMode,
      });
      setNotice(`Booking request raised for plot ${selected.plot_number}.`);
      setSelected(null);
      setTokenAmount("");
      setNewName("");
      setNewPhone("");
      const fresh = await fetchProject(session.token, project!.id);
      setProject(fresh);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not raise booking.");
    } finally {
      setBusy(false);
    }
  }

  if (!project) {
    return (
      <main className="container">
        <div className="loading">{error ? error : "Loading project…"}</div>
      </main>
    );
  }

  const total = project.total_plots || 1;

  return (
    <main className="container">
      <button className="btn secondary small" onClick={() => router.push("/projects")}>
        ← All projects
      </button>

      <h1 className="page-title" style={{ marginTop: 14 }}>
        {project.name}
      </h1>
      <p className="page-sub">
        {project.code} · {project.location} · {project.description}
      </p>

      {notice && <div className="ok">{notice}</div>}
      {error && <div className="error">{error}</div>}

      <div className="stats">
        <div className="stat">
          <div className="v">{project.total_plots}</div>
          <div className="k">Total plots</div>
        </div>
        <div className="stat" style={{ borderLeftColor: "#2e7d32" }}>
          <div className="v">{project.available}</div>
          <div className="k">Available</div>
        </div>
        <div className="stat" style={{ borderLeftColor: "#f29e1b" }}>
          <div className="v">{project.on_hold}</div>
          <div className="k">On hold</div>
        </div>
        <div className="stat" style={{ borderLeftColor: "#c0392b" }}>
          <div className="v">{project.sold}</div>
          <div className="k">Sold</div>
        </div>
      </div>

      <div className="bar" style={{ maxWidth: 460 }}>
        <span className="a" style={{ width: `${(project.available / total) * 100}%` }} />
        <span className="h" style={{ width: `${(project.on_hold / total) * 100}%` }} />
        <span className="s" style={{ width: `${(project.sold / total) * 100}%` }} />
      </div>

      <h2 className="section-title">Plot availability</h2>
      <div className="legend" style={{ marginBottom: 14 }}>
        <span>
          <i className="dot" style={{ background: "#2e7d32" }} /> Available
        </span>
        <span>
          <i className="dot" style={{ background: "#f29e1b" }} /> On hold
        </span>
        <span>
          <i className="dot" style={{ background: "#c0392b" }} /> Sold
        </span>
      </div>

      <div className="plot-grid">
        {(project.plots ?? []).map((plot) => (
          <div
            key={plot.id}
            className={`plot ${plot.status}${
              selected?.id === plot.id ? " selected" : ""
            }`}
            onClick={() => {
              setSelected(plot);
              setError("");
            }}
          >
            <div className="num">{plot.plot_number}</div>
            <div className="meta">{plot.size_sq_yds} sq yd</div>
            <div className="meta">{plot.facing_display}</div>
            <div className="meta">{formatMoney(plot.total_cost)}</div>
            <div style={{ marginTop: 6 }}>
              <span className={`badge ${plot.status}`}>{plot.status.replace("_", " ")}</span>
            </div>
          </div>
        ))}
      </div>

      {selected && (
        <>
          <div className="drawer-backdrop" onClick={() => setSelected(null)} />
          <div className="drawer">
            <h3>Plot {selected.plot_number}</h3>
            <p className="muted" style={{ marginTop: 0 }}>
              {project.name} · {project.code}
            </p>

            <div className="price">{formatMoney(selected.total_cost)}</div>
            <p className="muted">Total cost including PLC and discount</p>

            <div style={{ margin: "16px 0" }}>
              <div className="kv">
                <span className="k">Plot size</span>
                <span className="v">{selected.size_sq_yds} sq yds</span>
              </div>
              <div className="kv">
                <span className="k">Facing</span>
                <span className="v">{selected.facing_display}</span>
              </div>
              <div className="kv">
                <span className="k">BSP</span>
                <span className="v">{formatMoney(selected.bsp)} / sq yd</span>
              </div>
              <div className="kv">
                <span className="k">PLC</span>
                <span className="v">{selected.plc_pct}%</span>
              </div>
              <div className="kv">
                <span className="k">Discount</span>
                <span className="v">{selected.discount_pct}%</span>
              </div>
              <div className="kv">
                <span className="k">Status</span>
                <span className="v">
                  <span className={`badge ${selected.status}`}>
                    {selected.status.replace("_", " ")}
                  </span>
                </span>
              </div>
            </div>

            {selected.status !== "available" ? (
              <div className="hint">This plot is not available for booking.</div>
            ) : (
              <form onSubmit={submitBooking}>
                <h4 style={{ margin: "6px 0 10px" }}>Raise booking request</h4>

                <div className="field">
                  <label>
                    <input
                      type="radio"
                      checked={!useNewCustomer}
                      onChange={() => setUseNewCustomer(false)}
                      style={{ width: "auto", marginRight: 6 }}
                    />
                    Select an existing customer
                  </label>
                  {customers.length === 0 && (
                    <p className="muted">No customers yet — register one below.</p>
                  )}
                  {!useNewCustomer && (
                    <select
                      value={customerId}
                      onChange={(e) => setCustomerId(e.target.value)}
                    >
                      <option value="">Select customer…</option>
                      {customers.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.name} — {c.phone}
                        </option>
                      ))}
                    </select>
                  )}
                </div>

                <div className="field">
                  <label>
                    <input
                      type="radio"
                      checked={useNewCustomer}
                      onChange={() => setUseNewCustomer(true)}
                      style={{ width: "auto", marginRight: 6 }}
                    />
                    Register a new customer
                  </label>
                  {useNewCustomer && (
                    <>
                      <input
                        placeholder="Full name"
                        value={newName}
                        onChange={(e) => setNewName(e.target.value)}
                      />
                      <input
                        placeholder="Phone"
                        value={newPhone}
                        onChange={(e) => setNewPhone(e.target.value)}
                        style={{ marginTop: 8 }}
                      />
                    </>
                  )}
                </div>

                <div className="field">
                  <label htmlFor="token">Token amount (₹)</label>
                  <input
                    id="token"
                    type="number"
                    min={1}
                    required
                    value={tokenAmount}
                    onChange={(e) => setTokenAmount(e.target.value)}
                    placeholder="250000"
                  />
                </div>

                <div className="field">
                  <label htmlFor="pmode">Payment mode</label>
                  <select
                    id="pmode"
                    value={paymentMode}
                    onChange={(e) => setPaymentMode(e.target.value)}
                  >
                    <option value="upi">UPI</option>
                    <option value="bank">Bank transfer</option>
                    <option value="cheque">Cheque</option>
                    <option value="cash">Cash</option>
                  </select>
                </div>

                <button className="btn" type="submit" disabled={busy} style={{ width: "100%" }}>
                  {busy ? "Submitting…" : "Submit booking request"}
                </button>
              </form>
            )}
          </div>
        </>
      )}
    </main>
  );
}
