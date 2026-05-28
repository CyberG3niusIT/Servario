import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Servario",
  description: "Self-hosted Terminbuchungssystem",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="de">
      <body>{children}</body>
    </html>
  );
}
