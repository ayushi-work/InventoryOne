"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../../../lib/auth";
import {
  createPlots,
  createProject,
  deletePlot,
  deleteProject,
  fetchAdminPlots,
  fetchAdminProjects,
  formatMoney,
  updatePlot,
  updateProject,
  type PlotInput,
  type Project,
} from "../../../lib/api";

const FACINGS = ["E", "W", "N", "S", "NE", "NW", "SE", "SW"];

const EMPTY_PLOT: PlotInput = {
  plot_number: "",
  size_sq_yds: "200",
  facing: "E",
  status: "available",
  bsp: "5000",
  plc_pct: "0",
  discount_pct: "0",
};

export default function AdminProjectsPage() {
  const { session, loading } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selected, setSelected] = useState<Project | null>(null);
  const [plots, setPlots] = useState<PlotInput[]>([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);

  // new project form
  const [np, setNp] = useState({ name: "", code: "", location: "", status: "active", description: "" });
  // new plot form
  const [plot, setPlot] = useState<PlotInput>({ ...EMPTY_PLOT });

  async function loadProjects() {
    if (!session) return;
    const data = await fetchAdminProjects(session.token).catch(() => []);
    setProjects(data);
    if (data.length && !selected) setSelected(data[0]);
  }

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
    fetchAdminProjects(session.token)
      .then((data) => {
        setProjects(data);
        setSelected((prev) => prev ?? data[0] ?? null);
      })
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Could not load projects.")
      );
  }, [session, loading]);

  useEffect(() => {
    if (!session || !selected) return;
    fetchAdminPlots(session.token, selected.id)
      .then(setPlots)
      .catch(() => undefined);
  }, [session, selected]);

  async function submitProject(e: React.FormEvent) {
    e.preventDefault();
    if (!session) return;
    setError("");
    setNotice("");
    setBusy(true);
    try {
      const created = await createProject(session.token, np);
      setNp({ name: "", code: "", location: "", status: "active", description: "" });
      await loadProjects();
      setSelected(created);
      setNotice(`Project "${created.name}" created and brokers notified.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create the project.");
    } finally {
      setBusy(false);
    }
  }

  async function submitPlot(e: React.FormEvent) {
    e.preventDefault();
    if (!session || !selected) return;
    setError("");
    setNotice("");
    setBusy(true);
    try {
      await createPlots(session.token, selected.id, [plot]);
      setPlot({ ...EMPTY_PLOT });
      const fresh = await fetchAdminPlots(session.token, selected.id);
      setPlots(fresh);
      setNotice(`Plot ${plot.plot_number} added to ${selected.name}.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add the plot.");
    } finally {
      setBusy(false);
    }
  }

  async function removePlot(id: number) {
    if (!session) return;
    try {
      await deletePlot(session.token, id);
      setPlots((prev) => prev.filter((p) => p.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete the plot.");
    }
  }

  async function savePlot(id: number, changes: Partial<PlotInput>) {
    if (!session) return;
    try {
      await updatePlot(session.token, id, changes);
      const fresh = await fetchAdminPlots(session.token, selected!.id);
      setPlots(fresh);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update the plot.");
    }
  }

  async function removeProject(id: number) {
    if (!session) return;
    try {
      await deleteProject(session.token, id);
      const data = await fetchAdminProjects(session.token);
      setProjects(data);
      setSelected(data[0] ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete the project.");
    }
  }

  return (
    <main className="container">
      <h1 className="page-title">Project & Inventory Management</h1>
      <p className="page-sub">Create projects, maintain the plot grid and control availability.</p>

      {notice && <div className="ok">{notice}</div>}
      {error && <div className="error">{error}</div>}

      <div className="row" style={{ alignItems: "flex-start" }}>
        <div className="card" style={{ flex: "0 0 320px" }}>
          <h3>Create project</h3>
          <form onSubmit={submitProject}>
            <div className="field">
              <label htmlFor="pname">Name *</label>
              <input id="pname" required value={np.name}
                     onChange={(e) => setNp({ ...np, name: e.target.value })} />
            </div>
            <div className="field">
              <label htmlFor="pcode">Code *</label>
              <input id="pcode" required value={np.code}
                     onChange={(e) => setNp({ ...np, code: e.target.value.toUpperCase() })} />
            </div>
            <div className="field">
              <label htmlFor="ploc">Location</label>
              <input id="ploc" value={np.location}
                     onChange={(e) => setNp({ ...np, location: e.target.value })} />
            </div>
            <div className="field">
              <label htmlFor="pstat">Status</label>
              <select id="pstat" value={np.status}
                      onChange={(e) => setNp({ ...np, status: e.target.value })}>
                <option value="active">Active</option>
                <option value="upcoming">Upcoming</option>
                <option value="closed">Closed</option>
              </select>
            </div>
            <div className="field">
              <label htmlFor="pdesc">Description</label>
              <textarea id="pdesc" rows={2} value={np.description}
                        onChange={(e) => setNp({ ...np, description: e.target.value })} />
            </div>
            <button className="btn" type="submit" disabled={busy} style={{ width: "100%" }}>
              {busy ? "Creating…" : "Create project"}
            </button>
          </form>
        </div>

        <div style={{ flex: 1, minWidth: 340 }}>
          <h2 className="section-title" style={{ marginTop: 0 }}>
            Projects
          </h2>
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Project</th>
                  <th>Code</th>
                  <th>Plots</th>
                  <th>Available</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {projects.map((p) => (
                  <tr
                    key={p.id}
                    onClick={() => setSelected(p)}
                    style={{
                      cursor: "pointer",
                      background: selected?.id === p.id ? "#eef6f5" : undefined,
                    }}
                  >
                    <td>
                      <strong>{p.name}</strong>
                      <div className="muted">{p.location}</div>
                    </td>
                    <td>{p.code}</td>
                    <td>{p.total_plots}</td>
                    <td>{p.available}</td>
                    <td>
                      <span className="badge available">{p.status}</span>
                    </td>
                    <td>
                      <button
                        className="btn danger small"
                        onClick={(e) => {
                          e.stopPropagation();
                          void removeProject(p.id);
                        }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {selected && (
            <>
              <h2 className="section-title">
                Plot inventory — {selected.name} ({plots.length})
              </h2>

              <div className="card" style={{ marginBottom: 16 }}>
                <h3>Add a plot</h3>
                <form onSubmit={submitPlot}>
                  <div className="row">
                    <div className="field">
                      <label>Number</label>
                      <input value={plot.plot_number}
                             onChange={(e) => setPlot({ ...plot, plot_number: e.target.value })} />
                    </div>
                    <div className="field">
                      <label>Size (sq yd)</label>
                      <input value={plot.size_sq_yds}
                             onChange={(e) => setPlot({ ...plot, size_sq_yds: e.target.value })} />
                    </div>
                    <div className="field">
                      <label>Facing</label>
                      <select value={plot.facing}
                              onChange={(e) => setPlot({ ...plot, facing: e.target.value })}>
                        {FACINGS.map((f) => (
                          <option key={f} value={f}>{f}</option>
                        ))}
                      </select>
                    </div>
                    <div className="field">
                      <label>BSP</label>
                      <input value={plot.bsp}
                             onChange={(e) => setPlot({ ...plot, bsp: e.target.value })} />
                    </div>
                    <div className="field">
                      <label>PLC %</label>
                      <input value={plot.plc_pct}
                             onChange={(e) => setPlot({ ...plot, plc_pct: e.target.value })} />
                    </div>
                    <div className="field">
                      <label>Discount %</label>
                      <input value={plot.discount_pct}
                             onChange={(e) => setPlot({ ...plot, discount_pct: e.target.value })} />
                    </div>
                  </div>
                  <button className="btn" type="submit" disabled={busy}>
                    {busy ? "Adding…" : "Add plot"}
                  </button>
                </form>
              </div>

              <div className="table-wrap" style={{ maxHeight: 420, overflowY: "auto" }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Plot</th>
                      <th>Size</th>
                      <th>Facing</th>
                      <th>BSP</th>
                      <th>Status</th>
                      <th>Total</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {plots.map((p) => (
                      <tr key={p.id}>
                        <td>
                          <strong>{p.plot_number}</strong>
                        </td>
                        <td>{p.size_sq_yds}</td>
                        <td>{p.facing}</td>
                        <td>{formatMoney(p.bsp)}</td>
                        <td>
                          <select
                            value={p.status}
                            onChange={(e) =>
                              p.id !== undefined && void savePlot(p.id, { status: e.target.value })
                            }
                            style={{ padding: "4px 6px", borderRadius: 6, border: "1px solid var(--line)" }}
                          >
                            <option value="available">available</option>
                            <option value="on_hold">on hold</option>
                            <option value="sold">sold</option>
                          </select>
                        </td>
                        <td>
                          {formatMoney(
                            Number(p.size_sq_yds) * Number(p.bsp) *
                            (1 + Number(p.plc_pct) / 100) * (1 - Number(p.discount_pct) / 100)
                          )}
                        </td>
                        <td>
                          <button
                            className="btn danger small"
                            onClick={() => p.id !== undefined && void removePlot(p.id)}
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      </div>
    </main>
  );
}
