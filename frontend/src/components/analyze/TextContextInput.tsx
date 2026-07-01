"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Send, Loader2 } from "lucide-react";

interface Props {
  onAnalyze: (text: string) => void;
  loading: boolean;
}

export function TextContextInput({ onAnalyze, loading }: Props) {
  const [text, setText] = useState("");

  const handleSubmit = () => {
    if (!text.trim() || loading) return;
    onAnalyze(text.trim());
  };

  return (
    <div className="w-full max-w-xl mx-auto space-y-4">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Pega aqu&iacute; la conversaci&oacute;n o el contexto que quieras analizar..."
        rows={6}
        className="w-full p-4 rounded-xl border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 dark:placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-violet-500 resize-none transition-shadow"
      />
      <motion.button
        onClick={handleSubmit}
        disabled={!text.trim() || loading}
        whileTap={{ scale: 0.97 }}
        className="w-full py-3 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-medium shadow-lg hover:shadow-xl hover:scale-[1.02] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <Loader2 size={20} className="animate-spin" />
            Analizando...
          </>
        ) : (
          <>
            <Send size={18} />
            Analizar conversaci&oacute;n
          </>
        )}
      </motion.button>
    </div>
  );
}
