"use client";

import React, { useState } from "react";
import { SpectralProfile } from "@/data/benchmarkScenes";
import { Info, Sparkles } from "lucide-react";

interface SpectralSignatureChartProps {
  profiles: SpectralProfile[];
}

export const SpectralSignatureChart: React.FC<SpectralSignatureChartProps> = ({ profiles }) => {
  const [activeBand, setActiveBand] = useState<SpectralProfile | null>(profiles[7]); // Default to B8 NIR

  // Dimensions for SVG Line Chart
  const width = 640;
  const height = 180;
  const padding = { top: 20, right: 30, bottom: 35, left: 45 };

  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;

  // Max reflectance is ~0.6
  const maxY = 0.6;

  // Helper to map index to X coordinate
  const getX = (index: number) => padding.left + (index / (profiles.length - 1)) * chartW;
  // Helper to map value to Y coordinate
  const getY = (val: number) => padding.top + chartH - (val / maxY) * chartH;

  // Generate SVG path strings for the three spectral curves
  const makePath = (key: "water" | "vegetation" | "soil") => {
    return profiles.reduce((acc, p, i) => {
      const x = getX(i);
      const y = getY(p[key]);
      return `${acc} ${i === 0 ? "M" : "L"} ${x},${y}`;
    }, "");
  };

  return (
    <div className="glass-panel border-t border-slate-800/80 px-4 lg:px-8 py-4 bg-space-950/90">
      <div className="max-w-7xl mx-auto flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-5">
        {/* Left: Section Header & Physics Insight */}
        <div className="max-w-xs shrink-0">
          <div className="flex items-center gap-1.5 text-xs font-mono text-hydro-blue mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>12-Band Spectral Signature</span>
          </div>
          <h4 className="text-sm font-bold text-white tracking-tight">
            Physical Reflectance Curves
          </h4>
          <p className="text-xs text-slate-400 mt-1 leading-relaxed">
            Observe the steep absorption drop of water in <strong className="text-hydro-blue">B8 NIR</strong> and <strong className="text-sky-400">B11/B12 SWIR</strong>, proving why multispectral inputs vastly outperform standard 3-channel RGB.
          </p>

          {/* Legend */}
          <div className="flex items-center gap-3 mt-3 text-[11px] font-mono">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-hydro-cyan" />
              <span className="text-slate-300 font-semibold">Water</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
              <span className="text-slate-400">Vegetation</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
              <span className="text-slate-400">Arid Soil</span>
            </div>
          </div>
        </div>

        {/* Center: Interactive SVG Spectral Chart */}
        <div className="flex-1 overflow-x-auto">
          <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-44 max-w-2xl mx-auto">
            {/* Grid Lines */}
            {[0, 0.2, 0.4, 0.6].map((tick) => {
              const y = getY(tick);
              return (
                <g key={tick}>
                  <line
                    x1={padding.left}
                    y1={y}
                    x2={width - padding.right}
                    y2={y}
                    stroke="#1e293b"
                    strokeDasharray="3,3"
                  />
                  <text
                    x={padding.left - 8}
                    y={y + 3}
                    textAnchor="end"
                    fill="#64748b"
                    fontSize="9"
                    fontFamily="monospace"
                  >
                    {tick.toFixed(1)}
                  </text>
                </g>
              );
            })}

            {/* Band Columns & Labels */}
            {profiles.map((p, i) => {
              const x = getX(i);
              const isSelected = activeBand?.band === p.band;
              return (
                <g
                  key={p.band}
                  className="cursor-pointer"
                  onClick={() => setActiveBand(p)}
                >
                  <line
                    x1={x}
                    y1={padding.top}
                    x2={x}
                    y2={padding.top + chartH}
                    stroke={isSelected ? "#00E5FF" : "transparent"}
                    strokeWidth="1.5"
                    strokeDasharray="2,2"
                  />
                  <text
                    x={x}
                    y={height - 12}
                    textAnchor="middle"
                    fill={isSelected ? "#00E5FF" : "#94a3b8"}
                    fontSize="10"
                    fontWeight={isSelected ? "bold" : "normal"}
                    fontFamily="monospace"
                  >
                    {p.band}
                  </text>
                </g>
              );
            })}

            {/* Curves */}
            <path
              d={makePath("soil")}
              fill="none"
              stroke="#f59e0b"
              strokeWidth="2"
              opacity="0.7"
            />
            <path
              d={makePath("vegetation")}
              fill="none"
              stroke="#f43f5e"
              strokeWidth="2"
              opacity="0.8"
            />
            <path
              d={makePath("water")}
              fill="none"
              stroke="#00E5FF"
              strokeWidth="3"
              className="drop-shadow-[0_0_8px_rgba(0,229,255,0.6)]"
            />

            {/* Data Points on Curves */}
            {profiles.map((p, i) => {
              const x = getX(i);
              return (
                <g key={p.band}>
                  <circle cx={x} cy={getY(p.soil)} r="2.5" fill="#f59e0b" />
                  <circle cx={x} cy={getY(p.vegetation)} r="2.5" fill="#f43f5e" />
                  <circle cx={x} cy={getY(p.water)} r="3.5" fill="#00E5FF" />
                </g>
              );
            })}
          </svg>
        </div>

        {/* Right: Active Band Detail Card */}
        {activeBand && (
          <div className="w-52 shrink-0 p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-xs font-mono space-y-1.5 shadow-md">
            <div className="flex items-center justify-between pb-1 border-b border-slate-800 text-slate-300">
              <span className="font-bold text-white">{activeBand.band}</span>
              <span className="text-[10px] text-slate-400">{activeBand.name} ({activeBand.wavelength} µm)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-hydro-blue">Water:</span>
              <span className="font-bold text-white">{(activeBand.water * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-rose-400">Vegetation:</span>
              <span className="text-slate-300">{(activeBand.vegetation * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-amber-400">Soil:</span>
              <span className="text-slate-300">{(activeBand.soil * 100).toFixed(1)}%</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
