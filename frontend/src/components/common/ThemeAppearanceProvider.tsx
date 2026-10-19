"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

type ThemeMode = "light" | "dark" | "system";
type AccentColor = "zinc" | "blue" | "violet" | "emerald" | "rose";

interface AppearanceContextType {
  theme: ThemeMode;
  accent: AccentColor;
  setTheme: (t: ThemeMode) => void;
  setAccent: (a: AccentColor) => void;
}

const AppearanceContext = createContext<AppearanceContextType | null>(null);

export function ThemeAppearanceProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<ThemeMode>("system");
  const [accent, setAccentState] = useState<AccentColor>("zinc");

  useEffect(() => {
    const cachedTheme = (localStorage.getItem("ui_theme") as ThemeMode) || "system";
    const cachedAccent = (localStorage.getItem("ui_accent") as AccentColor) || "zinc";
    setThemeState(cachedTheme);
    setAccentState(cachedAccent);

    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (token) {
      apiClient
        .get("/users/me/preferences")
        .then(({ data }) => {
          if (data.theme_mode) setThemeState(data.theme_mode);
          if (data.accent_color) setAccentState(data.accent_color);
        })
        .catch(() => {});
    }
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove("light", "dark");

    if (theme === "system") {
      const systemDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      root.classList.add(systemDark ? "dark" : "light");
    } else {
      root.classList.add(theme);
    }

    root.dataset.accent = accent;
  }, [theme, accent]);

  const setTheme = (t: ThemeMode) => {
    setThemeState(t);
    localStorage.setItem("ui_theme", t);
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (token) apiClient.patch("/users/me/preferences", { theme_mode: t }).catch(() => {});
  };

  const setAccent = (a: AccentColor) => {
    setAccentState(a);
    localStorage.setItem("ui_accent", a);
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (token) apiClient.patch("/users/me/preferences", { accent_color: a }).catch(() => {});
  };

  return (
    <AppearanceContext.Provider value={{ theme, accent, setTheme, setAccent }}>
      {children}
    </AppearanceContext.Provider>
  );
}

export const useAppearance = () => {
  const ctx = useContext(AppearanceContext);
  if (!ctx) throw new Error("useAppearance must be used within ThemeAppearanceProvider");
  return ctx;
};