"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
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

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (raw) setSession(JSON.parse(raw) as Session);
    } catch {
      window.localStorage.removeItem(STORAGE_KEY);
    }
    setLoading(false);
  }, []);

  const requestCode = useCallback(async (email: string) => {
    const res = await requestOtp(email);
    return { devCode: res.dev_code };
  }, []);

  const login = useCallback(async (email: string, code: string) => {
    const res = await verifyOtp(email, code);
    const next: Session = { token: res.token, role: res.role, broker: res.broker };
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    setSession(next);
  }, []);

  const logout = useCallback(() => {
    window.localStorage.removeItem(STORAGE_KEY);
    setSession(null);
  }, []);

  const value = useMemo(
    () => ({ session, loading, requestCode, login, logout }),
    [session, loading, requestCode, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
