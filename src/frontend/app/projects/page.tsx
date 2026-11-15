"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuth } from "../../lib/auth";
import { fetchProjects, type Project } from "../../lib/api";

export default function ProjectsPage() {
  const { session, loading } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [error, setError] = useState("");

  useEffect(() => {
    if (loading) return;
    if (!session) {
      window.location.href = "/";
      return;
    }
    fetchProjects(session.token)
      .then((data) => {
        setProjects(data);
        setState("ready");
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Failed to load projects.");
        setState("error");
      });
  }, [session, loading]);

  if (state === "loading") return <div className="loading">Loading projects…</div>;

  return (
    <main className="container">
      <h1 className="page-title">Active Projects</h1>
      <p className="page-sub">
        Live plot availability across all active projects. Green = available, amber = on hold, red =
        sold.
      </p>

      {state === "error" && <div className="error">{error}</div>}

      <div className="legend" style={{ marginBottom: 16 }}>
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

      {projects.length === 0 && state === "ready" && (
        <div className="card">No active projects yet.</div>
      )}

      <div className="card-grid">
        {projects.map((p) => {
          const total = p.total_plots || 1;
          return (
            <Link href={`/projects/${p.id}`} key={p.id}>
              <div className="card">
                <h3>{p.name}</h3>
                <p className="muted" style={{ margin: "0 0 6px" }}>
                  {p.code} · {p.location}
                </p>
                <p className="muted" style={{ margin: 0 }}>
                  {p.description}
                </p>
                <div className="bar">
                  <span className="a" style={{ width: `${(p.available / total) * 100}%` }} />
                  <span className="h" style={{ width: `${(p.on_hold / total) * 100}%` }} />
                  <span className="s" style={{ width: `${(p.sold / total) * 100}%` }} />
                </div>
                <div className="legend">
                  <span>{p.available} available</span>
                  <span>{p.on_hold} on hold</span>
                  <span>{p.sold} sold</span>
                  <span style={{ marginLeft: "auto", fontWeight: 700 }}>
                    {p.total_plots} plots
                  </span>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </main>
  );
}
