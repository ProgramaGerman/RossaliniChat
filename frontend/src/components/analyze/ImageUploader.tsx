"use client";

import { useState, useRef, useCallback } from "react";
import { motion } from "framer-motion";
import { ImageUp, X, Loader2 } from "lucide-react";

interface Props {
  onAnalyze: (file: File) => void;
  loading: boolean;
}

export function ImageUploader({ onAnalyze, loading }: Props) {
  const [preview, setPreview] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    if (!f.type.startsWith("image/")) return;
    setFile(f);
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target?.result as string);
    reader.readAsDataURL(f);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const f = e.dataTransfer.files[0];
      if (f) handleFile(f);
    },
    [handleFile]
  );

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => setDragging(false);

  const clear = () => {
    setPreview(null);
    setFile(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div className="w-full max-w-xl mx-auto">
      {!preview ? (
        <motion.div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          animate={{
            scale: dragging ? 1.02 : 1,
            borderColor: dragging ? "#8b5cf6" : undefined,
          }}
          className="relative flex flex-col items-center gap-4 p-12 rounded-2xl border-2 border-dashed border-zinc-300 dark:border-zinc-700 cursor-pointer hover:border-violet-500 dark:hover:border-violet-400 transition-colors"
          onClick={() => inputRef.current?.click()}
        >
          <div className="p-4 rounded-full bg-violet-100 dark:bg-violet-900/30">
            <ImageUp size={32} className="text-violet-600 dark:text-violet-400" />
          </div>
          <p className="text-zinc-600 dark:text-zinc-400">
            Arrastra una captura o haz clic para seleccionar
          </p>
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) handleFile(f);
            }}
          />
        </motion.div>
      ) : (
        <div className="relative rounded-2xl overflow-hidden border border-zinc-300 dark:border-zinc-700">
          <img
            src={preview}
            alt="Preview"
            className="w-full h-auto max-h-96 object-contain bg-zinc-100 dark:bg-zinc-900"
          />
          <div className="absolute top-3 right-3 flex gap-2">
            <button
              onClick={clear}
              className="p-2 rounded-full bg-black/60 text-white hover:bg-black/80 transition-colors"
            >
              <X size={18} />
            </button>
          </div>
        </div>
      )}
      {file && !loading && (
        <motion.button
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          onClick={() => onAnalyze(file)}
          className="mt-4 w-full py-3 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-medium shadow-lg hover:shadow-xl hover:scale-[1.02] transition-all duration-200"
        >
          Analizar conversaci&oacute;n
        </motion.button>
      )}
      {loading && (
        <div className="mt-4 flex items-center justify-center gap-2 py-3 text-violet-600 dark:text-violet-400">
          <Loader2 size={22} className="animate-spin" />
          <span>Analizando conversaci&oacute;n...</span>
        </div>
      )}
    </div>
  );
}
