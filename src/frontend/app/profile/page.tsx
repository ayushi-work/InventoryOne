"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../../lib/auth";
import { fetchMe, updateMe, type Broker } from "../../lib/api";

const EMPTY = {
  phone: "",
  pan_number: "",
  aadhaar_number: "",
  gst_number: "",
  rera_number: "",
  bank_account: "",
  ifsc: "",
  agreement_accepted: false,
};

export default function ProfilePage() {
  const { session, loading } = useAuth();
  const [profile, setProfile] = useState<Broker | null>(null);
  const [form, setForm] = useState({ ...EMPTY });
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (loading) return;
    if (!session) {
      window.location.href = "/";
      return;
    }
    fetchMe(session.token)
      .then((b) => {
        setProfile(b);
        setForm({
          phone: b.phone || "",
          pan_number: b.pan_number || "",
          aadhaar_number: b.aadhaar_number || "",
          gst_number: b.gst_number || "",
          rera_number: b.rera_number || "",
          bank_account: b.bank_account || "",
          ifsc: b.ifsc || "",
          agreement_accepted: b.agreement_accepted,
        });
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load profile."));
  }, [session, loading]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!session) return;
    setError("");
    setNotice("");
    setBusy(true);
    try {
      const updated = await updateMe(session.token, form);
      setProfile(updated);
      setNotice("KYC details saved. Status is under company review.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save profile.");
    } finally {
      setBusy(false);
    }
  }

  function set(key: keyof typeof form, value: string | boolean) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  if (!profile) {
    return (
      <main className="container">
        <div className="loading">{error || "Loading profile…"}</div>
      </main>
    );
  }

  return (
    <main className="container">
      <h1 className="page-title">Broker Profile & KYC</h1>
      <p className="page-sub">
        Your verification status is shown below. Keep documents and bank details up to date so
        bookings get approved faster.
      </p>

      {notice && <div className="ok">{notice}</div>}
      {error && <div className="error">{error}</div>}

      <div className="row" style={{ alignItems: "flex-start" }}>
        <div className="card" style={{ flex: "0 0 300px" }}>
          <h3>Account</h3>
          <div className="kv">
            <span className="k">Name</span>
            <span className="v">{profile.name}</span>
          </div>
          <div className="kv">
            <span className="k">Email</span>
            <span className="v">{profile.email}</span>
          </div>
          <div className="kv">
            <span className="k">KYC status</span>
            <span className="v">
              <span className={`badge ${profile.kyc_status}`}>{profile.kyc_status}</span>
            </span>
          </div>
          <div className="kv">
            <span className="k">Agreement</span>
            <span className="v">{profile.agreement_accepted ? "Accepted" : "Not accepted"}</span>
          </div>
        </div>

        <div className="card" style={{ flex: 1, minWidth: 320 }}>
          <h3>KYC & bank details</h3>
          <form onSubmit={submit}>
            <div className="row">
              <div className="field">
                <label htmlFor="p">Phone</label>
                <input id="p" value={form.phone} onChange={(e) => set("phone", e.target.value)} />
              </div>
              <div className="field">
                <label htmlFor="pan">PAN number</label>
                <input
                  id="pan"
                  value={form.pan_number}
                  onChange={(e) => set("pan_number", e.target.value)}
                />
              </div>
            </div>
            <div className="row">
              <div className="field">
                <label htmlFor="aadhaar">Aadhaar number</label>
                <input
                  id="aadhaar"
                  value={form.aadhaar_number}
                  onChange={(e) => set("aadhaar_number", e.target.value)}
                />
              </div>
              <div className="field">
                <label htmlFor="gst">GST number</label>
                <input
                  id="gst"
                  value={form.gst_number}
                  onChange={(e) => set("gst_number", e.target.value)}
                />
              </div>
            </div>
            <div className="row">
              <div className="field">
                <label htmlFor="rera">RERA number</label>
                <input
                  id="rera"
                  value={form.rera_number}
                  onChange={(e) => set("rera_number", e.target.value)}
                />
              </div>
              <div className="field">
                <label htmlFor="bank">Bank account</label>
                <input
                  id="bank"
                  value={form.bank_account}
                  onChange={(e) => set("bank_account", e.target.value)}
                />
              </div>
              <div className="field">
                <label htmlFor="ifsc">IFSC</label>
                <input
                  id="ifsc"
                  value={form.ifsc}
                  onChange={(e) => set("ifsc", e.target.value)}
                />
              </div>
            </div>
            <div className="field">
              <label style={{ fontWeight: 400 }}>
                <input
                  type="checkbox"
                  checked={form.agreement_accepted}
                  onChange={(e) => set("agreement_accepted", e.target.checked)}
                  style={{ width: "auto", marginRight: 8 }}
                />
                I accept the broker agreement
              </label>
            </div>
            <button className="btn" type="submit" disabled={busy}>
              {busy ? "Saving…" : "Save details"}
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
