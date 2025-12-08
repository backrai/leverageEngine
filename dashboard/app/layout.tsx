import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'backrAI Creator Dashboard',
  description: 'Leverage data for creators',
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

