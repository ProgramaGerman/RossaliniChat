"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { MessageSquareText, ImageUp } from "lucide-react";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.15, delayChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: "easeOut" as const },
  },
};

export function HeroSection() {
  return (
    <section className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] px-6 text-center">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="max-w-3xl"
      >
        <motion.h1
          variants={itemVariants}
          className="text-5xl md:text-7xl font-bold tracking-tight bg-gradient-to-r from-violet-600 via-fuchsia-500 to-indigo-500 bg-clip-text text-transparent"
        >
          RossalinChat
        </motion.h1>
        <motion.p
          variants={itemVariants}
          className="mt-6 text-lg md:text-xl text-zinc-600 dark:text-zinc-400 leading-relaxed"
        >
          Analiza conversaciones reales de WhatsApp, Instagram y m&aacute;s.
          Obt&eacute;n respuestas inteligentes en 6 modos &uacute;nicos.
        </motion.p>
        <motion.div
          variants={itemVariants}
          className="mt-10 flex flex-col sm:flex-row gap-4 justify-center"
        >
          <Link
            href="/analyze"
            className="inline-flex items-center gap-2 px-8 py-3 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-medium shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200"
          >
            <ImageUp size={20} />
            Subir captura
          </Link>
          <Link
            href="/analyze?mode=text"
            className="inline-flex items-center gap-2 px-8 py-3 rounded-xl border border-zinc-300 dark:border-zinc-700 text-zinc-800 dark:text-zinc-200 font-medium hover:bg-zinc-100 dark:hover:bg-zinc-800 hover:scale-105 transition-all duration-200"
          >
            <MessageSquareText size={20} />
            Escribir contexto
          </Link>
        </motion.div>
      </motion.div>
    </section>
  );
}
