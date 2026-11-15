"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../../lib/auth";
import { createCustomer, fetchCustomers, formatDate, type Customer } from "../../lib/api";

export default function CustomersPage() {
  const { session, loading } = useAuth();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [address, setAddress] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (loading) return;
    if (!session) {
      window.location.href = "/";
      return;
    }
    fetchCustomers(session.token)
      .then(setCustomers)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load customers."));
  }, [session, loading]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!session) return;
    setError("");
    setNotice("");
    setBusy(true);
    try {
      const created = await createCustomer(session.token, { name, phone, email, address });
      setCustomers((prev) => [created, ...prev]);
      setName("");
      setPhone("");
      setEmail("");
      setAddress("");
      setNotice(`Customer "${created.name}" registered.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not register customer.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="container">
      <h1 className="page-title">Customers</h1>
      <p className="page-sub">
        Register customers so bookings can be linked to them. Every customer you register stays
        linked to your broker account.
      </p>

      {notice && <div className="ok">{notice}</div>}
      {error && <div className="error">{error}</div>}

      <div className="row" style={{ alignItems: "flex-start" }}>
        <div className="card" style={{ flex: "0 0 340px" }}>
          <h3>Register customer</h3>
          <form onSubmit={submit}>
            <div className="field">
              <label htmlFor="cname">Full name *</label>
              <input
                id="cname"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="cphone">Phone *</label>
              <input
                id="cphone"
                required
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="cmail">Email</label>
              <input
                id="cmail"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="caddr">Address</label>
              <textarea
                id="caddr"
                rows={2}
                value={address}
                onChange={(e) => setAddress(e.target.value)}
              />
            </div>
            <button className="btn" type="submit" disabled={busy} style={{ width: "100%" }}>
              {busy ? "Saving…" : "Register customer"}
            </button>
          </form>
        </div>

        <div style={{ flex: 1, minWidth: 320 }}>
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Phone</th>
                  <th>Email</th>
                  <th>Registered</th>
                </tr>
              </thead>
              <tbody>
                {customers.length === 0 && (
                  <tr>
                    <td colSpan={4} className="muted">
                      No customers registered yet.
                    </td>
                  </tr>
                )}
                {customers.map((c) => (
                  <tr key={c.id}>
                    <td>
                      <strong>{c.name}</strong>
                      {c.address && <div className="muted">{c.address}</div>}
                    </td>
                    <td>{c.phone}</td>
                    <td>{c.email || "—"}</td>
                    <td>{formatDate(c.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  );
}
