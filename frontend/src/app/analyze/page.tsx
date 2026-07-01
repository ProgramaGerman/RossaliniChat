"use client";

import { useState, useCallback, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { ImageUp, MessageSquareText } from "lucide-react";
import { ImageUploader } from "@/components/analyze/ImageUploader";
import { TextContextInput } from "@/components/analyze/TextContextInput";
import { ResultsGrid } from "@/components/results/ResultsGrid";
import { LoadingSkeleton } from "@/components/results/LoadingSkeleton";
import { analyzeImage, analyzeText, fetchModes } from "@/lib/api";
import type { ModeInfo, AnalyzeResponse } from "@/lib/types";

function AnalyzeContent() {
  const searchParams = useSearchParams();
  const initialMode = searchParams.get("mode") === "text" ? "text" : "image";
  const [inputMode, setInputMode] = useState<"image" | "text">(initialMode);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [modes, setModes] = useState<ModeInfo[]>([]);

  useEffect(() => {
    fetchModes()
      .then(setModes)
      .catch(() => {});
  }, []);

  const handleImageAnalyze = useCallback(async (file: File) => {
    setLoading(true);
    setResult(null);
    try {
      const data = await analyzeImage(file);
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleTextAnalyze = useCallback(async (text: string) => {
    setLoading(true);
    setResult(null);
    try {
      const data = await analyzeText(text);
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <div className="min-h-[calc(100vh-4rem)] px-6 py-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold">Analizar conversaci&oacute;n</h1>
          <p className="text-zinc-500 dark:text-zinc-400">
            Sube una captura de pantalla o escribe el contexto
          </p>
        </div>

        <div className="flex justify-center gap-2 p-1 rounded-xl bg-zinc-100 dark:bg-zinc-900 w-fit mx-auto">
          <button
            onClick={() => setInputMode("image")}
            className={`flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-medium transition-all ${
              inputMode === "image"
                ? "bg-white dark:bg-zinc-800 shadow-sm text-zinc-900 dark:text-zinc-100"
                : "text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300"
            }`}
          >
            <ImageUp size={18} />
            Subir captura
          </button>
          <button
            onClick={() => setInputMode("text")}
            className={`flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-medium transition-all ${
              inputMode === "text"
                ? "bg-white dark:bg-zinc-800 shadow-sm text-zinc-900 dark:text-zinc-100"
                : "text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300"
            }`}
          >
            <MessageSquareText size={18} />
            Escribir contexto
          </button>
        </div>

        <AnimatePresence mode="wait">
          {inputMode === "image" ? (
            <motion.div
              key="image"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
            >
              <ImageUploader onAnalyze={handleImageAnalyze} loading={loading} />
            </motion.div>
          ) : (
            <motion.div
              key="text"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <TextContextInput onAnalyze={handleTextAnalyze} loading={loading} />
            </motion.div>
          )}
        </AnimatePresence>

        {loading && <LoadingSkeleton />}

        {result && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <h2 className="text-xl font-semibold text-center">Resultados</h2>
            <ResultsGrid results={result.modes} modes={modes} />
          </motion.div>
        )}
      </div>
    </div>
  );
}

export default function AnalyzePage() {
  return (
    <Suspense fallback={<LoadingSkeleton />}>
      <AnalyzeContent />
    </Suspense>
  );
}
