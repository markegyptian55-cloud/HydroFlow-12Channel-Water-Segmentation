import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HydroFlow | Multispectral Satellite Water Intelligence & AI Segmentation",
  description: "Executive geospatial dashboard for Sentinel-2 MSI water body extraction and Optimal Transport Flow Matching (OT-CFM) generative intelligence.",
  keywords: ["Sentinel-2", "Remote Sensing", "Water Segmentation", "Deep Learning", "PyTorch", "Flow Matching", "GIS"],
  authors: [{ name: "Mohamed Mostafa Elbasyouni", url: "https://github.com/markegyptian55-cloud" }],
  openGraph: {
    title: "HydroFlow | Multispectral Satellite Water Intelligence",
    description: "Executive geospatial dashboard for Sentinel-2 water segmentation with 72.62% IoU and +3.18% CFM generative gain.",
    siteName: "HydroFlow",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-space-950 text-slate-100 antialiased selection:bg-hydro-cyan/30 selection:text-white">
        {children}
      </body>
    </html>
  );
}
