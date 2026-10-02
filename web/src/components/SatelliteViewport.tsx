"use client";

import React, { useState, useRef, useEffect } from "react";
import { BenchmarkScene } from "@/data/benchmarkScenes";
import { ZoomIn, ZoomOut, RotateCcw, Crosshair, Eye, Compass, Move } from "lucide-react";

export type SpectralLayer = "rgb" | "nir" | "ndwi" | "mask" | "cfm";

interface SatelliteViewportProps {
  scene: BenchmarkScene;
  activeLayer: SpectralLayer;
  confidenceThreshold: number;
}

export const SatelliteViewport: React.FC<SatelliteViewportProps> = ({
  scene,
  activeLayer,
  confidenceThreshold,
}) => {
  const [sliderPos, setSliderPos] = useState<number>(50);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const containerRef = useRef<HTMLDivElement>(null);

  // Mouse & Touch Drag Handlers for Split Screen Slider
  const handleMove = (clientX: number) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const pos = ((clientX - rect.left) / rect.width) * 100;
    setSliderPos(Math.min(Math.max(pos, 2), 98));
  };

  const onMouseMove = (e: React.MouseEvent) => {
    if (isDragging) handleMove(e.clientX);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    if (isDragging && e.touches[0]) handleMove(e.touches[0].clientX);
  };

  useEffect(() => {
    const handleMouseUp = () => setIsDragging(false);
    window.addEventListener("mouseup", handleMouseUp);
    window.addEventListener("touchend", handleMouseUp);
    return () => {
      window.removeEventListener("mouseup", handleMouseUp);
      window.removeEventListener("touchend", handleMouseUp);
    };
  }, []);

  // Layer Renderer based on spectral physics
  const renderLayerVisuals = (layer: SpectralLayer, isRightSide: boolean = false) => {
    switch (layer) {
      case "rgb":
        // Natural Color: Realistic soil/desert land and deep turquoise water
        return (
          <div className="absolute inset-0 w-full h-full bg-gradient-to-br from-amber-900/40 via-yellow-950/60 to-stone-900">
            <svg viewBox="0 0 600 600" className="w-full h-full object-cover">
              {/* Land Texture Patterns */}
              <defs>
                <radialGradient id={`sand-${isRightSide ? "r" : "l"}`} cx="70%" cy="30%" r="80%">
                  <stop offset="0%" stopColor="#78350f" stopOpacity="0.8" />
                  <stop offset="50%" stopColor="#451a03" stopOpacity="0.9" />
                  <stop offset="100%" stopColor="#1c1917" stopOpacity="1" />
                </radialGradient>
                <linearGradient id={`water-rgb-${isRightSide ? "r" : "l"}`} x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#083344" />
                  <stop offset="50%" stopColor="#0e7490" />
                  <stop offset="100%" stopColor="#155e75" />
                </linearGradient>
              </defs>
              <rect width="600" height="600" fill={`url(#sand-${isRightSide ? "r" : "l"})`} />
              {/* Natural Water Body */}
              <path d={scene.svgPathWater} fill={`url(#water-rgb-${isRightSide ? "r" : "l"})`} opacity="0.95" />
              {/* Subtle Shoreline Sediment */}
              <path d={scene.svgPathCoastline} stroke="#fbbf24" strokeWidth="2.5" fill="none" opacity="0.4" />
            </svg>
          </div>
        );

      case "nir":
        // False-Color Infrared (B8, B4, B3): Vegetation appears vibrant crimson, water is pitch black
        return (
          <div className="absolute inset-0 w-full h-full bg-gradient-to-br from-red-950/80 via-rose-900/60 to-zinc-950">
            <svg viewBox="0 0 600 600" className="w-full h-full object-cover">
              <defs>
                <radialGradient id="nir-veg" cx="50%" cy="50%" r="70%">
                  <stop offset="0%" stopColor="#991b1b" />
                  <stop offset="70%" stopColor="#4c0519" />
                  <stop offset="100%" stopColor="#18181b" />
                </radialGradient>
              </defs>
              <rect width="600" height="600" fill="url(#nir-veg)" />
              {/* Water absorbs 100% of Near-Infrared */}
              <path d={scene.svgPathWater} fill="#020617" opacity="0.98" />
              <path d={scene.svgPathCoastline} stroke="#e11d48" strokeWidth="3" fill="none" opacity="0.6" />
            </svg>
          </div>
        );

      case "ndwi":
        // NDWI Heatmap: Fluid gradient from deep navy to bright cyan
        return (
          <div className="absolute inset-0 w-full h-full bg-gradient-to-br from-amber-950/60 via-stone-900 to-black">
            <svg viewBox="0 0 600 600" className="w-full h-full object-cover">
              <defs>
                <linearGradient id="ndwi-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#00E5FF" />
                  <stop offset="60%" stopColor="#0284c7" />
                  <stop offset="100%" stopColor="#0369a1" />
                </linearGradient>
              </defs>
              <rect width="600" height="600" fill="#292524" opacity="0.9" />
              <path d={scene.svgPathWater} fill="url(#ndwi-gradient)" opacity="0.95" />
              <path d={scene.svgPathCoastline} stroke="#38bdf8" strokeWidth="4" strokeDasharray="6,3" fill="none" opacity="0.8" />
            </svg>
          </div>
        );

      case "mask":
        // HydroFlow Neural U-Net Segmentation Mask
        return (
          <div className="absolute inset-0 w-full h-full bg-slate-950/90">
            <svg viewBox="0 0 600 600" className="w-full h-full object-cover">
              <defs>
                <filter id="neon-glow" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="5" result="blur" />
                  <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>
              {/* Background Sentinel-2 Satellite Image */}
              <rect width="600" height="600" fill="#0f172a" />
              {/* Segmented Water Area with Confidence Opacity */}
              <path
                d={scene.svgPathWater}
                fill="#00E5FF"
                fillOpacity={Math.max(0.4, confidenceThreshold)}
              />
              {/* Radiant Shoreline Boundary Glow */}
              <path
                d={scene.svgPathCoastline}
                stroke="#00E5FF"
                strokeWidth="3.5"
                fill="none"
                filter="url(#neon-glow)"
              />
            </svg>
          </div>
        );

      case "cfm":
        // OT-CFM Generative Synthetic Reconstruction
        return (
          <div className="absolute inset-0 w-full h-full bg-gradient-to-br from-indigo-950/60 via-slate-900 to-sky-950/70">
            <svg viewBox="0 0 600 600" className="w-full h-full object-cover">
              <rect width="600" height="600" fill="#1e1b4b" opacity="0.8" />
              <path d={scene.svgPathWater} fill="#0284c7" opacity="0.9" />
              {/* Flow Matching Vector Streamlines */}
              <path d={scene.svgPathCoastline} stroke="#818cf8" strokeWidth="2" strokeDasharray="4,4" fill="none" opacity="0.7" />
            </svg>
          </div>
        );
    }
  };

  return (
    <div className="relative flex-1 flex flex-col h-full bg-space-950 select-none overflow-hidden">
      {/* Top Telemetry Overlay */}
      <div className="absolute top-4 left-4 z-20 flex items-center gap-2 pointer-events-auto">
        <div className="glass-panel px-3 py-1.5 rounded-lg border border-slate-700/60 flex items-center gap-2 text-xs font-mono shadow-lg">
          <Compass className="w-3.5 h-3.5 text-hydro-blue animate-spin" style={{ animationDuration: "12s" }} />
          <span className="text-slate-300">{scene.coordinatesDisplay}</span>
          <span className="text-slate-600">|</span>
          <span className="text-emerald-400 font-semibold">{scene.region}</span>
        </div>

        <div className="hidden sm:flex glass-panel px-2.5 py-1.5 rounded-lg border border-slate-700/60 items-center gap-1.5 text-xs font-mono text-slate-300">
          <span className="w-2 h-2 rounded-full bg-hydro-blue animate-ping" />
          <span>Sentinel-2 (10m GSD)</span>
        </div>
      </div>

      {/* Top Right Viewport Controls */}
      <div className="absolute top-4 right-4 z-20 flex items-center gap-1.5 pointer-events-auto">
        <button
          onClick={() => setZoomLevel((z) => Math.min(z + 0.25, 2.5))}
          className="glass-panel p-2 rounded-lg border border-slate-700/60 hover:border-hydro-cyan/50 text-slate-300 hover:text-white transition-all shadow-md"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => setZoomLevel((z) => Math.max(z - 0.25, 0.75))}
          className="glass-panel p-2 rounded-lg border border-slate-700/60 hover:border-hydro-cyan/50 text-slate-300 hover:text-white transition-all shadow-md"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={() => {
            setZoomLevel(1);
            setSliderPos(50);
          }}
          className="glass-panel p-2 rounded-lg border border-slate-700/60 hover:border-hydro-cyan/50 text-slate-300 hover:text-white transition-all shadow-md"
          title="Reset View"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* Main Interactive Split-Screen Viewport */}
      <div
        ref={containerRef}
        onMouseMove={onMouseMove}
        onTouchMove={onTouchMove}
        className="relative flex-1 w-full h-full cursor-col-resize overflow-hidden satellite-grid"
      >
        <div
          className="w-full h-full transition-transform duration-200 ease-out origin-center"
          style={{ transform: `scale(${zoomLevel})` }}
        >
          {/* Base Layer (Right of Slider): Ground Truth Natural Color RGB */}
          <div className="absolute inset-0 w-full h-full pointer-events-none">
            {renderLayerVisuals("rgb", true)}
          </div>

          {/* Active Layer (Left of Slider): Clipped dynamically by sliderPos */}
          <div
            className="absolute inset-0 h-full overflow-hidden pointer-events-none"
            style={{ width: `${sliderPos}%` }}
          >
            <div className="relative w-full h-full" style={{ width: containerRef.current?.clientWidth || "100%" }}>
              {renderLayerVisuals(activeLayer, false)}
            </div>
          </div>
        </div>

        {/* Vertical Split-Screen Divider & Draggable Handle */}
        <div
          className="absolute top-0 bottom-0 z-30 flex items-center justify-center pointer-events-none"
          style={{ left: `${sliderPos}%`, transform: "translateX(-50%)" }}
        >
          {/* Glowing Vertical Line */}
          <div className="w-[2px] h-full bg-gradient-to-b from-transparent via-hydro-cyan to-transparent shadow-[0_0_12px_#00E5FF]" />

          {/* Center Circular Grab Handle */}
          <div
            onMouseDown={() => setIsDragging(true)}
            onTouchStart={() => setIsDragging(true)}
            className="pointer-events-auto absolute w-8 h-8 rounded-full bg-slate-900 border-2 border-hydro-cyan shadow-[0_0_16px_rgba(0,229,255,0.6)] flex items-center justify-center cursor-grab active:cursor-grabbing hover:scale-110 transition-transform"
          >
            <Move className="w-3.5 h-3.5 text-hydro-blue rotate-45" />
          </div>
        </div>

        {/* Layer Comparison Labels */}
        <div className="absolute bottom-5 left-5 z-20 pointer-events-none">
          <div className="glass-panel px-3 py-1.5 rounded-lg border border-slate-700/80 text-xs font-mono text-hydro-blue shadow-lg">
            Active: <span className="text-white uppercase font-bold">{activeLayer}</span>
          </div>
        </div>

        <div className="absolute bottom-5 right-5 z-20 pointer-events-none">
          <div className="glass-panel px-3 py-1.5 rounded-lg border border-slate-700/80 text-xs font-mono text-slate-400 shadow-lg">
            Reference: <span className="text-slate-200 uppercase font-semibold">Natural RGB</span>
          </div>
        </div>

        {/* Center Crosshair Scale Indicator */}
        <div className="absolute bottom-5 left-1/2 -translate-x-1/2 z-20 pointer-events-none hidden md:flex items-center gap-2 glass-panel px-3 py-1 rounded-md text-[11px] font-mono text-slate-400">
          <Crosshair className="w-3 h-3 text-hydro-blue" />
          <span>Scale: 10 km</span>
          <div className="w-12 h-1 bg-slate-600 rounded-full overflow-hidden">
            <div className="w-1/2 h-full bg-hydro-cyan" />
          </div>
        </div>
      </div>
    </div>
  );
};
