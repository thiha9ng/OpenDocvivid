import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "sonner";
import { Providers } from "@/components/providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "DocVivid - Convert Technical Documentation to AI Videos | Instant Video Creation",
  description: "Transform technical documentation into engaging AI-narrated videos in minutes. Perfect for developers, tech writers, and educators. High-quality output with customizable voices and professional visuals.",
  keywords: ["technical documentation to video", "AI video generator", "developer documentation videos", "code explanation videos", "technical content creation", "API documentation videos", "AI narration", "developer tools", "technical tutorials", "documentation automation"],
  authors: [{ name: "DocVivid Team" }],
  viewport: "width=device-width, initial-scale=1",
  robots: "index, follow, max-image-preview:large",
  alternates: {
    canonical: "https://aidocvivid.com",
  },
  openGraph: {
    title: "DocVivid - Convert Technical Documentation to AI Videos | Developer Tool",
    description: "Transform technical docs, code explanations, and API guides into professional AI-narrated videos. Save hours of video creation time with our specialized tech content video generator.",
    type: "website",
    locale: "en_US",
    url: "https://aidocvivid.com",
    siteName: "DocVivid",
    images: [
      {
        url: "https://aidocvivid.com/logo.png",
        width: 1200,
        height: 630,
        alt: "DocVivid - Technical Documentation to Video Converter",
      }
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "DocVivid - Technical Documentation to AI Video Converter",
    description: "Convert complex technical content into clear, engaging AI-narrated videos. Perfect for developers, tech writers and engineering teams.",
    creator: "@docvividai",
    images: ["https://aidocvivid.com/logo.png"],
  },
};

import StructuredData from './structured-data';

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="canonical" href="https://aidocvivid.com" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <Providers>
          <Toaster position="top-center" richColors/>
          {children}
          <StructuredData />
        </Providers>
      </body>
    </html>
  );
}
