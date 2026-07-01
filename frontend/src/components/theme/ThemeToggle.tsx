"use client";

import { useTheme } from "next-themes";
import { Sun, Moon } from "lucide-react";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  if (!mounted) return <div className="w-9 h-9" />;

  return (
    <motion.button
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      className="relative p-2 rounded-full hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors"
      whileTap={{ scale: 0.9 }}
      animate={{ rotate: theme === "dark" ? 180 : 0 }}
      transition={{ type: "spring", stiffness: 200, damping: 15 }}
      aria-label="Toggle theme"
    >
      {theme === "dark" ? <Moon size={20} /> : <Sun size={20} />}
    </motion.button>
  );
}
