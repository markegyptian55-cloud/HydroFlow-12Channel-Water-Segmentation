"use client";

import React from "react";
import { BENCHMARK_SCENES, BenchmarkScene } from "@/data/benchmarkScenes";
import { SpectralLayer } from "./SatelliteViewport";
import { Layers, Sparkles, Sliders, Globe2, Eye, Flame, Wand2, ShieldCheck } from "lucide-react";

interface LayerControlsProps {
  selectedScene: BenchmarkScene;
  onSelectScene: (scene: BenchmarkScene) => void;
  activeLayer: SpectralLayer;
  onSelectLayer: (layer: SpectralLayer) => void;
  confidenceThreshold: number;
  onChangeThreshold: (val: number) => void;
}

export const LayerControls: React.FC<LayerControlsProps> = ({
  selectedScene,
  onSelectScene,
  activeLayer,
  onSelectLayer,
  confidenceThreshold,
  onChangeThreshold,
}) => {
  const layers: { id: SpectralLayer; name: string; tag: string; icon: React.ReactNode; desc: string }[] = [
    {
      id: "mask",
      name: "HydroFlow AI",
      tag: "Deep U-Net",
      icon: <Sparkles className="w-4 h-4 text-hydro-blue" />,
      desc: "Deep neural segmentation mask with precision shoreline delineation (72.62% IoU).",
    },
    {
      id: "rgb",
      name: "Natural RGB",
      tag: "B4-B3-B2",
      icon: <Eye className="w-4 h-4 text-emerald-400" />,
      desc: "True human visual perception using 10m visible wavelength bands.",
    },
    {
      id: "nir",
      name: "False-Color NIR",
      tag: "B8-B4-B3",
      icon: <Flame className="w-4 h-4 text-rose-400" />,
      desc: "Extreme water absorption (black) vs high chlorophyll vegetation reflectance (crimson).",
    },
    {
      id: "ndwi",
      name: "NDWI Index",
      tag: "(G-NIR)/(G+NIR)",
      icon: <Layers className="w-4 h-4 text-sky-400" />,
      desc: "Physical McFeeters Normalized Difference Water Index highlighting water bodies.",
    },
    {
      id: "cfm",
      name: "OT-CFM Twin",
      tag: "Generative AI",
      icon: <Wand2 className="w-4 h-4 text-indigo-400" />,
      desc: "Continuous-time Flow Matching synthetic scene reconstruction from orphan masks (+3.18% boost).",
    },
  ];

  return (
    <div className="glass-panel border-b border-slate-800/80 px-4 lg:px-8 py-3 bg-space-900/90">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        {/* Scene Selector Dropdown */}
        <div className="flex items-center gap-2 min-w-fit">
          <Globe2 className="w-4 h-4 text-slate-400 shrink-0" />
          <span className="text-xs text-slate-400 font-mono hidden sm:inline">Scene:</span>
          <select
            value={selectedScene.id}
            onChange={(e) => {
              const target = BENCHMARK_SCENES.find((s) => s.id === e.target.value);
              if (target) onSelectScene(target);
            }}
            className="bg-slate-950/90 text-slate-100 text-xs rounded-lg px-3 py-1.5 border border-slate-700 hover:border-hydro-cyan/50 focus:outline-none focus:ring-1 focus:ring-hydro-cyan transition-all font-medium cursor-pointer"
          >
            {BENCHMARK_SCENES.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.country})
              </option>
            ))}
          </select>
        </div>

        {/* Spectral Layer Selector Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0 scrollbar-none">
          {layers.map((l) => {
            const isSelected = activeLayer === l.id;
            return (
              <button
                key={l.id}
                onClick={() => onSelectLayer(l.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all shrink-0 border ${
                  isSelected
                    ? "bg-hydro-cyan/10 border-hydro-cyan/50 text-white shadow-[0_0_12px_rgba(0,229,255,0.15)]"
                    : "bg-slate-950/50 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700"
                }`}
                title={l.desc}
              >
                {l.icon}
                <span>{l.name}</span>
                <span className="text-[10px] font-mono opacity-60 hidden xl:inline">
                  [{l.tag}]
                </span>
              </button>
            );
          })}
        </div>

        {/* Dynamic Confidence Threshold Slider (for AI Mask) */}
        {activeLayer === "mask" && (
          <div className="flex items-center gap-2.5 bg-slate-950/70 border border-slate-800 rounded-lg px-3 py-1 text-xs">
            <Sliders className="w-3.5 h-3.5 text-hydro-blue shrink-0" />
            <span className="text-slate-400 font-mono text-[11px] shrink-0">Threshold:</span>
            <input
              type="range"
              min="0.2"
              max="0.8"
              step="0.05"
              value={confidenceThreshold}
              onChange={(e) => onChangeThreshold(parseFloat(e.target.value))}
              className="w-20 accent-hydro-blue cursor-pointer h-1.5 bg-slate-800 rounded-lg"
            />
            <span className="font-mono text-hydro-blue font-semibold w-8 text-right">
              {(confidenceThreshold * 100).toFixed(0)}%
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
