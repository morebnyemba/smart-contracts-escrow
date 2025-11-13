import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Smart Contracts Escrow Platform",
  description: "Button-driven escrow platform with milestone-based payments",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
