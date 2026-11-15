"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  useSyncExternalStore,
  type ReactNode,
} from "react";
import { requestOtp, verifyOtp, type Broker, type Role } from "./api";

type Session = {
  token: string;
  role: Role;
  broker: Broker;
};

type AuthContextValue = {
  session: Session | null;
  loading: boolean;
  requestCode: (email: string) => Promise<{ devCode?: string }>;
  login: (email: string, code: string) => Promise<void>;
  logout: () => void;
};

const STORAGE_KEY = "inventoryone.session";

let cachedRaw: string | null = null;
let cachedSession: Session | null = null;

/* --- session store ------------------------------------------------------
 * The session lives in localStorage. Reading it through
 * useSyncExternalStore keeps every component in sync (including across
 * browser tabs) without setting state inside an effect.
 * ----------------------------------------------------------------------- */

function readSession(): Session | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(STORAGE_KEY);

  // The snapshot handed to useSyncExternalStore must be referentially stable,
  // otherwise React re-renders on every store read. Cache the parsed session
  // and only re-parse when the stored string actually changes.
  if (raw === cachedRaw) return cachedSession;

  cachedRaw = raw;
  try {
    cachedSession = raw ? (JSON.parse(raw) as Session) : null;
  } catch {
    cachedSession = null;
  }
  return cachedSession;
}

function subscribeToSession(callback: () => void) {
  window.addEventListener("storage", callback);
  window.addEventListener("inventoryone-session", callback);
  return () => {
    window.removeEventListener("storage", callback);
    window.removeEventListener("inventoryone-session", callback);
  };
}

function getServerSession(): Session | null {
  return null;
}

/** Stable no-op subscription used for the hydration flag. */
const noopSubscribe = () => () => {};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const session = useSyncExternalStore(
    subscribeToSession,
    readSession,
    getServerSession
  );

  // false during server rendering / hydration, true once mounted in the browser
  const hydrated = useSyncExternalStore(
    noopSubscribe,
    () => true,
    () => false
  );

  const requestCode = useCallback(async (email: string) => {
    const res = await requestOtp(email);
    return { devCode: res.dev_code };
  }, []);

  const login = useCallback(async (email: string, code: string) => {
    const res = await verifyOtp(email, code);
    const next: Session = { token: res.token, role: res.role, broker: res.broker };
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    window.dispatchEvent(new Event("inventoryone-session"));
  }, []);

  const logout = useCallback(() => {
    window.localStorage.removeItem(STORAGE_KEY);
    window.dispatchEvent(new Event("inventoryone-session"));
  }, []);

  const value = useMemo(
    () => ({ session, loading: !hydrated, requestCode, login, logout }),
    [session, hydrated, requestCode, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
