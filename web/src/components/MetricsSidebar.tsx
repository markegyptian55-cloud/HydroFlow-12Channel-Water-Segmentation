"use client";

import React, { useState } from "react";
import { BenchmarkScene } from "@/data/benchmarkScenes";
import { Droplets, Activity, Ruler, Download, CheckCircle, ShieldAlert, Cpu } from "lucide-react";

interface MetricsSidebarProps {
  scene: BenchmarkScene;
}

export const MetricsSidebar: React.FC<MetricsSidebarProps> = ({ scene }) => {
  const [downloadSuccess, setDownloadSuccess] = useState<string | null>(null);

  const handleExport = (format: "tif" | "png" | "geojson") => {
    setDownloadSuccess(format);
    setTimeout(() => setDownloadSuccess(null), 2500);
  };

  return (
    <aside className="w-full lg:w-80 glass-panel border-l border-slate-800/80 p-5 flex flex-col gap-5 overflow-y-auto bg-space-950/80">
      {/* Scene Overview Card */}
      <div>
        <div className="flex items-center justify-between text-xs text-slate-400 font-mono mb-1">
          <span>{scene.country}</span>
          <span className="text-slate-500">{scene.captureDate}</span>
        </div>
        <h2 className="text-base font-bold text-white tracking-tight leading-snug">
          {scene.name}
        </h2>
        <p className="text-xs text-slate-400 mt-1 leading-relaxed">
          {scene.description}
        </p>
      </div>

      <div className="h-[1px] bg-slate-800/60" />

      {/* Geospatial Hydrological Telemetry */}
      <div className="space-y-3.5">
        <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <Activity className="w-3.5 h-3.5 text-hydro-cyan" />
          <span>Geospatial Telemetry</span>
        </h3>

        {/* Water Surface Area Card */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/90 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="flex items-center gap-1.5">
              <Droplets className="w-3.5 h-3.5 text-hydro-blue" />
              Water Surface Area
            </span>
            <span className="font-mono text-[10px] text-slate-500">10m GSD</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white tracking-tight">
              {scene.waterAreaKm2.toLocaleString()}
            </span>
            <span className="text-xs text-slate-400 font-mono">km²</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            ≈ {(scene.waterAreaKm2 * 100).toLocaleString()} Hectares
          </p>
        </div>

        {/* Shoreline Perimeter Card */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/90 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="flex items-center gap-1.5">
              <Ruler className="w-3.5 h-3.5 text-amber-400" />
              Shoreline Perimeter
            </span>
            <span className="font-mono text-[10px] text-slate-500">Fractal Vector</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-xl font-bold font-mono text-white tracking-tight">
              {scene.shorelineKm.toLocaleString()}
            </span>
            <span className="text-xs text-slate-400 font-mono">km</span>
          </div>
        </div>

        {/* Model Accuracy & Confidence Gauge */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/90 shadow-sm space-y-2.5">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-emerald-400" />
              Segmentation Confidence
            </span>
            <span className="font-mono text-emerald-400 font-semibold">
              {scene.meanConfidence}%
            </span>
          </div>
          {/* Progress Bar */}
          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 rounded-full transition-all duration-500"
              style={{ width: `${scene.meanConfidence}%` }}
            />
          </div>
          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-0.5">
            <span>Validation IoU:</span>
            <span className="text-hydro-blue font-bold">{scene.validationIoU}%</span>
          </div>
        </div>
      </div>

      <div className="h-[1px] bg-slate-800/60" />

      {/* Export & Data Integration Actions */}
      <div className="space-y-2 mt-auto">
        <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <Download className="w-3.5 h-3.5 text-slate-400" />
          <span>GIS Data Exports</span>
        </h3>

        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => handleExport("tif")}
            className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-xs text-slate-200 hover:text-white transition-all font-medium"
          >
            {downloadSuccess === "tif" ? (
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
            ) : (
              <Download className="w-3.5 h-3.5 text-hydro-blue" />
            )}
            <span>6-Band TIFF</span>
          </button>

          <button
            onClick={() => handleExport("png")}
            className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-xs text-slate-200 hover:text-white transition-all font-medium"
          >
            {downloadSuccess === "png" ? (
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
            ) : (
              <Download className="w-3.5 h-3.5 text-hydro-cyan" />
            )}
            <span>AI Mask (PNG)</span>
          </button>
        </div>

        {downloadSuccess && (
          <div className="text-[11px] font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-800/50 rounded-lg p-2 text-center animate-fade-in">
            Exported {downloadSuccess.toUpperCase()} layer package successfully!
          </div>
        )}
      </div>

      {/* Corporate Division Badge */}
      <div className="p-3 rounded-xl bg-gradient-to-br from-cyan-950/40 to-slate-900 border border-cyan-800/30 text-[11px] text-slate-300">
        <span className="font-semibold text-hydro-cyan block mb-0.5">Cellula Technologies</span>
        Applied Remote Sensing & Generative Earth Observation Division
      </div>
    </aside>
  );
};
