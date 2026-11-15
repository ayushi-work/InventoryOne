"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../../lib/auth";
import {
  deleteDocument,
  fetchDocuments,
  fetchProjects,
  formatDate,
  generatePriceList,
  uploadKycDocument,
  type Document,
  type Project,
} from "../../lib/api";

const KYC_KINDS = [
  { value: "kyc_pan", label: "PAN card" },
  { value: "kyc_aadhaar", label: "Aadhaar card" },
  { value: "kyc_gst", label: "GST certificate" },
  { value: "kyc_cancelled_cheque", label: "Cancelled cheque" },
];

export default function DocumentsPage() {
  const { session, loading } = useAuth();
  const [docs, setDocs] = useState<Document[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [kind, setKind] = useState("kyc_pan");
  const [file, setFile] = useState<File | null>(null);
  const [projectId, setProjectId] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (loading) return;
    if (!session) {
      window.location.href = "/";
      return;
    }
    fetchDocuments(session.token)
      .then(setDocs)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load files."));
    fetchProjects(session.token)
      .then(setProjects)
      .catch(() => undefined);
  }, [session, loading]);

  async function upload(e: React.FormEvent) {
    e.preventDefault();
    if (!session || !file) return;
    setError("");
    setNotice("");
    setBusy(true);
    try {
      const form = new FormData();
      form.append("kind", kind);
      form.append("title", file.name);
      form.append("file", file);
      const created = await uploadKycDocument(session.token, form);
      setDocs((prev) => [created, ...prev]);
      setFile(null);
      setNotice(`Uploaded "${created.title}" (${created.size_kb} KB).`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setBusy(false);
    }
  }

  async function makePriceList(e: React.FormEvent) {
    e.preventDefault();
    if (!session || !projectId) return;
    setError("");
    setNotice("");
    setBusy(true);
    try {
      const doc = await generatePriceList(session.token, Number(projectId));
      setDocs((prev) => [doc, ...prev]);
      setNotice(`Price list generated for ${doc.title}.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not generate the price list.");
    } finally {
      setBusy(false);
    }
  }

  async function remove(id: number) {
    if (!session) return;
    try {
      await deleteDocument(session.token, id);
      setDocs((prev) => prev.filter((d) => d.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete the file.");
    }
  }

  const kycDocs = docs.filter((d) => d.kind.startsWith("kyc_"));
  const otherDocs = docs.filter((d) => !d.kind.startsWith("kyc_"));

  return (
    <main className="container">
      <h1 className="page-title">Documents</h1>
      <p className="page-sub">
        Upload your KYC files and download price lists, forms and demand letters.
      </p>

      {notice && <div className="ok">{notice}</div>}
      {error && <div className="error">{error}</div>}

      <div className="row" style={{ alignItems: "flex-start" }}>
        <div className="card" style={{ flex: "0 0 340px" }}>
          <h3>Upload a KYC document</h3>
          <form onSubmit={upload}>
            <div className="field">
              <label htmlFor="kind">Document type</label>
              <select id="kind" value={kind} onChange={(e) => setKind(e.target.value)}>
                {KYC_KINDS.map((k) => (
                  <option key={k.value} value={k.value}>
                    {k.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="file">File (PDF or image, max 10 MB)</label>
              <input
                id="file"
                type="file"
                accept=".pdf,.png,.jpg,.jpeg"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              />
            </div>
            <button className="btn" type="submit" disabled={busy || !file} style={{ width: "100%" }}>
              {busy ? "Uploading…" : "Upload"}
            </button>
          </form>

          <hr style={{ border: 0, borderTop: "1px solid var(--line)", margin: "18px 0" }} />

          <h3>Generate price list</h3>
          <form onSubmit={makePriceList}>
            <div className="field">
              <label htmlFor="proj">Project</label>
              <select id="proj" value={projectId} onChange={(e) => setProjectId(e.target.value)}>
                <option value="">Select project…</option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>
            <button
              className="btn secondary"
              type="submit"
              disabled={busy || !projectId}
              style={{ width: "100%" }}
            >
              Generate PDF
            </button>
          </form>
        </div>

        <div style={{ flex: 1, minWidth: 320 }}>
          <h2 className="section-title" style={{ marginTop: 0 }}>
            My KYC files
          </h2>
          {kycDocs.length === 0 ? (
            <div className="card">No KYC documents uploaded yet.</div>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Document</th>
                    <th>Type</th>
                    <th>Size</th>
                    <th>Uploaded</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {kycDocs.map((d) => (
                    <tr key={d.id}>
                      <td>
                        <strong>{d.title}</strong>
                      </td>
                      <td>{d.kind_display}</td>
                      <td>{d.size_kb} KB</td>
                      <td>{formatDate(d.created_at)}</td>
                      <td>
                        <div style={{ display: "flex", gap: 6 }}>
                          <a className="btn small" href={d.download_url} target="_blank" rel="noreferrer">
                            Open
                          </a>
                          <button className="btn danger small" onClick={() => remove(d.id)}>
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <h2 className="section-title">Price lists & letters</h2>
          {otherDocs.length === 0 ? (
            <div className="card">No downloads yet — generate a price list above.</div>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Document</th>
                    <th>Type</th>
                    <th>Size</th>
                    <th>Created</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {otherDocs.map((d) => (
                    <tr key={d.id}>
                      <td>
                        <strong>{d.title}</strong>
                      </td>
                      <td>{d.kind_display}</td>
                      <td>{d.size_kb} KB</td>
                      <td>{formatDate(d.created_at)}</td>
                      <td>
                        <a className="btn small" href={d.download_url} target="_blank" rel="noreferrer">
                          Download
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
