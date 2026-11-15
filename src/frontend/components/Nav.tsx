"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "../lib/auth";
import NotificationBell from "./NotificationBell";

const BROKER_LINKS = [
  { href: "/projects", label: "Projects" },
  { href: "/bookings", label: "Bookings" },
  { href: "/customers", label: "Customers" },
  { href: "/commissions", label: "Commissions" },
  { href: "/documents", label: "Documents" },
  { href: "/support", label: "Support" },
  { href: "/profile", label: "KYC Profile" },
];

const ADMIN_LINKS = [
  { href: "/admin", label: "Dashboard" },
  { href: "/admin/bookings", label: "Bookings" },
  { href: "/admin/commissions", label: "Commissions" },
  { href: "/admin/projects", label: "Projects" },
  { href: "/admin/tickets", label: "Tickets" },
  { href: "/admin/brokers", label: "Brokers" },
  { href: "/admin/audit", label: "Audit" },
  { href: "/projects", label: "Inventory" },
];

export default function Nav() {
  const { session, loading, logout } = useAuth();
  const pathname = usePathname();

  if (loading) return <div className="nav" style={{ height: 58 }} />;
  if (!session) return null;

  const links = session.role === "admin" ? ADMIN_LINKS : BROKER_LINKS;

  return (
    <nav className="nav">
      <div className="nav-inner">
        <Link href="/" className="brand">
          Inventory<span>One</span>
        </Link>
        <div className="nav-links">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={`nav-link${
                pathname === l.href || pathname.startsWith(l.href + "/")
                  ? " active"
                  : ""
              }`}
            >
              {l.label}
            </Link>
          ))}
        </div>
        <div className="nav-right">
          <NotificationBell />
          <span>
            {session.broker.name || session.broker.email}
            <span
              className="badge"
              style={{
                marginLeft: 8,
                background: session.role === "admin" ? "#2e9e8f" : "#2a487a",
              }}
            >
              {session.role}
            </span>
          </span>
          <button className="btn secondary small" onClick={logout}>
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
