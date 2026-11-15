"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuth } from "../lib/auth";

export default function LoginPage() {
  const { session, loading, requestCode, login } = useAuth();
  const router = useRouter();

  const [email, setEmail] = useState("broker@example.com");
  const [code, setCode] = useState("");
  const [stage, setStage] = useState<"email" | "code">("email");
  const [devCode, setDevCode] = useState<string | undefined>();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!loading && session) router.replace("/projects");
  }, [loading, session, router]);

  async function handleRequestOtp(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const { devCode: dc } = await requestCode(email.trim());
      setDevCode(dc);
      if (dc) setCode(dc);
      setStage("code");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not send OTP.");
    } finally {
      setBusy(false);
    }
  }

  async function handleVerify(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(email.trim(), code.trim());
      router.replace("/projects");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid OTP.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-wrap">
      <div className="login-card">
        <h1>InventoryOne</h1>
        <p className="sub">Broker Web App · Sign in with OTP</p>

        {error && <div className="error">{error}</div>}

        {stage === "email" ? (
          <form onSubmit={handleRequestOtp}>
            <div className="field">
              <label htmlFor="email">Registered email</label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="broker@example.com"
              />
            </div>
            <button className="btn" type="submit" disabled={busy} style={{ width: "100%" }}>
              {busy ? "Sending OTP…" : "Send OTP"}
            </button>
            <p className="muted" style={{ marginTop: 14 }}>
              New brokers are registered automatically on the first OTP request.
            </p>
          </form>
        ) : (
          <form onSubmit={handleVerify}>
            {devCode && (
              <div className="hint">
                Development mode — your OTP is <strong>{devCode}</strong> (email delivery is
                stubbed).
              </div>
            )}
            <div className="field">
              <label htmlFor="code">Enter OTP</label>
              <input
                id="code"
                inputMode="numeric"
                required
                maxLength={6}
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="6-digit code"
              />
            </div>
            <button className="btn" type="submit" disabled={busy} style={{ width: "100%" }}>
              {busy ? "Verifying…" : "Verify & Login"}
            </button>
            <button
              type="button"
              className="btn secondary"
              style={{ width: "100%", marginTop: 10 }}
              onClick={() => {
                setStage("email");
                setCode("");
                setDevCode(undefined);
              }}
            >
              Change email
            </button>
          </form>
        )}

        <p className="muted" style={{ marginTop: 18 }}>
          Admin: admin@inventoryone.local · Broker: broker@example.com
        </p>
      </div>
    </div>
  );
}
