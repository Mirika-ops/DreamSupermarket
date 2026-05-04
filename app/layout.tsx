import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "3D Exhibition - Particle Field",
  description: "Interactive 3D scene with dust particles, time-based model transformation, and digital clock",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
