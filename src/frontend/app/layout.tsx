import { Suspense } from "react";
import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "../lib/auth";
import Nav from "../components/Nav";

export const metadata: Metadata = {
  title: "InventoryOne — Broker Web App",
  description:
    "Real-estate plot booking platform for brokers: live inventory, bookings and commissions.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <div className="shell">
            <Suspense fallback={<div className="nav" style={{ height: 58 }} />}>
              <Nav />
            </Suspense>
            {children}
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
