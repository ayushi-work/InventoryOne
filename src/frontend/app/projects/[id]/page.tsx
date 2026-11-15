"use client";

import { Suspense } from "react";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuth } from "../../../lib/auth";
import { fetchProject, formatMoney, type Plot, type Project } from "../../../lib/api";

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
  const [selected, setSelected] = useState<Plot | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (loading) return;
    if (!session) {
      window.location.href = "/";
      return;
    }
    const id = params?.id;
    if (!id) return;
    fetchProject(session.token, id)
      .then(setProject)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load project."));
  }, [session, loading, params?.id]);

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
            className={`plot ${plot.status}${selected?.id === plot.id ? " selected" : ""}`}
            onClick={() => setSelected(plot)}
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
    </main>
  );
}
