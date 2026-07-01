import type { Metadata } from "next";
import { ThemeProvider } from "@/components/theme/ThemeProvider";
import { ThemeToggle } from "@/components/theme/ThemeToggle";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "RossalinChat",
  description:
    "Analiza conversaciones y obtén respuestas inteligentes en 6 modos únicos",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body className="min-h-screen bg-white dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100 antialiased">
        <ThemeProvider>
          <header className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 bg-white/80 dark:bg-zinc-950/80 backdrop-blur-md border-b border-zinc-200 dark:border-zinc-800">
            <a
              href="/"
              className="text-lg font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent"
            >
              RossalinChat
            </a>
            <ThemeToggle />
          </header>
          <main className="pt-16">{children}</main>
        </ThemeProvider>
      </body>
    </html>
  );
}
