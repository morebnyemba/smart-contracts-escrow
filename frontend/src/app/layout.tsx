import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Smart Contracts Escrow Platform",
  description: "Secure escrow platform for buyers and sellers",
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
