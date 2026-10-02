"use client";

import React from "react";
import { Satellite, Award, ExternalLink, Github, BarChart3, Database } from "lucide-react";

interface HeaderProps {
  onOpenBenchmark: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenBenchmark }) => {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-4 lg:px-8 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand & Mission Title */}
        <div className="flex items-center gap-3.5">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-hydro-cyan/20 to-blue-600/20 border border-hydro-cyan/30 text-hydro-blue shadow-lg shadow-hydro-cyan/10">
            <Satellite className="w-5 h-5 animate-pulse" />
            <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-hydro-cyan bg-clip-text text-transparent">
                HydroFlow
              </h1>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-cyan-950/80 text-hydro-cyan border border-cyan-800/50">
                Sentinel-2 MSI
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Multispectral Satellite Water Intelligence & Generative AI (OT-CFM)
            </p>
          </div>
        </div>

        {/* Quick KPI Badges & Actions */}
        <div className="flex items-center gap-2.5">
          {/* Benchmark Pill */}
          <button
            onClick={onOpenBenchmark}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-700/80 hover:border-hydro-cyan/50 text-xs font-mono transition-all text-slate-200 hover:text-white shadow-sm"
          >
            <Award className="w-3.5 h-3.5 text-amber-400" />
            <span className="hidden md:inline text-slate-400">IoU:</span>
            <span className="font-semibold text-hydro-blue">72.62%</span>
            <span className="text-[10px] text-emerald-400 bg-emerald-950/50 px-1 rounded border border-emerald-800/40">
              +3.18% CFM
            </span>
          </button>

          {/* Benchmark Details Modal Trigger */}
          <button
            onClick={onOpenBenchmark}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 text-xs text-blue-300 transition-colors font-medium"
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Benchmark</span>
          </button>

          {/* GitHub Repo Link */}
          <a
            href="https://github.com/markegyptian55-cloud/HydroFlow-12Channel-Water-Segmentation"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-700 text-xs text-slate-300 hover:text-white transition-colors"
          >
            <Github className="w-3.5 h-3.5" />
            <span className="hidden lg:inline">GitHub</span>
          </a>

          {/* Kaggle Suite Link */}
          <a
            href="https://www.kaggle.com/code/markegyptian/water-segmentation-flow-matching"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-700 text-xs text-slate-300 hover:text-white transition-colors"
          >
            <Database className="w-3.5 h-3.5 text-sky-400" />
            <span className="hidden lg:inline">Kaggle</span>
            <ExternalLink className="w-3 h-3 text-slate-500" />
          </a>
        </div>
      </div>
    </header>
  );
};
