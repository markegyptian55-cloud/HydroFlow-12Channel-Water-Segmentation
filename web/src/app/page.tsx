"use client";

import React, { useState } from "react";
import { Header } from "@/components/Header";
import { LayerControls } from "@/components/LayerControls";
import { SatelliteViewport, SpectralLayer } from "@/components/SatelliteViewport";
import { MetricsSidebar } from "@/components/MetricsSidebar";
import { SpectralSignatureChart } from "@/components/SpectralSignatureChart";
import { BenchmarkModal } from "@/components/BenchmarkModal";
import { BENCHMARK_SCENES, BenchmarkScene } from "@/data/benchmarkScenes";

export default function Home() {
  const [selectedScene, setSelectedScene] = useState<BenchmarkScene>(BENCHMARK_SCENES[0]);
  const [activeLayer, setActiveLayer] = useState<SpectralLayer>("mask");
  const [confidenceThreshold, setConfidenceThreshold] = useState<number>(0.5);
  const [isBenchmarkOpen, setIsBenchmarkOpen] = useState<boolean>(false);

  return (
    <main className="flex flex-col min-h-screen bg-space-950 text-slate-100 overflow-hidden">
      {/* 1. Global Navigation Bar */}
      <Header onOpenBenchmark={() => setIsBenchmarkOpen(true)} />

      {/* 2. Interactive Layer Controls & Scene Switcher */}
      <LayerControls
        selectedScene={selectedScene}
        onSelectScene={setSelectedScene}
        activeLayer={activeLayer}
        onSelectLayer={setActiveLayer}
        confidenceThreshold={confidenceThreshold}
        onChangeThreshold={setConfidenceThreshold}
      />

      {/* 3. Central Working Area: Satellite Viewport + GIS Metrics Sidebar */}
      <div className="flex-1 flex flex-col lg:flex-row min-h-[500px] h-[55vh] relative">
        <SatelliteViewport
          scene={selectedScene}
          activeLayer={activeLayer}
          confidenceThreshold={confidenceThreshold}
        />
        <MetricsSidebar scene={selectedScene} />
      </div>

      {/* 4. Bottom 12-Band Spectral Signature Analyzer */}
      <SpectralSignatureChart profiles={selectedScene.spectralProfiles} />

      {/* 5. Empirical Benchmark Modal */}
      <BenchmarkModal
        isOpen={isBenchmarkOpen}
        onClose={() => setIsBenchmarkOpen(false)}
      />
    </main>
  );
}
