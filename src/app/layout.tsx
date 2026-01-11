import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { TripPlanningProvider } from "@/contexts/TripPlanningContext";
import { PageErrorBoundary } from "@/components/PageErrorBoundary";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Travel Planner",
  description: "Create personalized travel itineraries with AI-powered planning and real-time transport data",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <PageErrorBoundary>
          <TripPlanningProvider>
            {children}
          </TripPlanningProvider>
        </PageErrorBoundary>
      </body>
    </html>
  );
}
