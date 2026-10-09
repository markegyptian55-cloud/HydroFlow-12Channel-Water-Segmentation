"""
HydroFlow Interactive Dashboard Builder
Generates reports/interactive_dashboard.html and dashboard.html with zero-dependency embedded data.
Includes 100% offline SVG fallback, mathematical linear epoch alignment, canvas warmup annotations,
best checkpoint markers, and interactive cross-chart model inspection.
"""

import json
import os

def load_data():
    with open('reports/data/benchmark_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def build_dashboard():
    data = load_data()
    data_json_str = json.dumps(data)

    html_content = f"""<!DOCTYPE html>
<html lang="en" class="dark scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HydroFlow | Multispectral Satellite Water Segmentation &amp; Generative CFM Dashboard</title>
    
    <!-- Meta tags -->
    <meta name="description" content="Interactive research dashboard showcasing Sentinel-2 12-channel multispectral water segmentation, Transfer Learning (ResNet-34 & EfficientNet-B0), and Generative Flow Matching.">
    <meta name="author" content="Mohamed Mostafa Elbasyouni">

    <!-- Tailwind CSS (via CDN) -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    colors: {{
                        slate: {{
                            850: '#151e2e',
                            950: '#070b14',
                        }},
                        hydro: {{
                            50: '#ecfeff',
                            100: '#cffafe',
                            400: '#22d3ee',
                            500: '#06b6d4',
                            600: '#0891b2',
                            900: '#164e63',
                        }},
                        emerald: {{
                            450: '#10b981',
                        }}
                    }},
                    fontFamily: {{
                        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
                        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
                    }}
                }}
            }}
        }};
    </script>

    <!-- Chart.js 4.x (via CDN) -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

    <style>
        /* Modern Glassmorphism & Custom Accents */
        :root {{
            --bg-deep: #0b0f19;
            --card-bg: rgba(17, 24, 39, 0.75);
            --card-border: rgba(255, 255, 255, 0.08);
            --card-hover-border: rgba(6, 182, 212, 0.4);
            --glow-cyan: rgba(6, 182, 212, 0.15);
            --glow-emerald: rgba(16, 185, 129, 0.15);
        }}

        body {{
            background-color: var(--bg-deep);
            color: #f3f4f6;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background-image: 
                radial-gradient(circle at 15% 10%, rgba(6, 182, 212, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 85% 25%, rgba(16, 185, 129, 0.06) 0%, transparent 40%),
                radial-gradient(circle at 50% 80%, rgba(139, 92, 246, 0.06) 0%, transparent 50%);
            background-attachment: fixed;
            min-height: 100vh;
        }}

        .glass-card {{
            background: var(--card-bg);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid var(--card-border);
            border-radius: 1rem;
            transition: all 0.25s ease-in-out;
        }}

        .glass-card:hover {{
            border-color: rgba(255, 255, 255, 0.16);
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        }}

        .model-card-btn {{
            cursor: pointer;
            border: 1px solid rgba(255, 255, 255, 0.08);
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .model-card-btn:hover {{
            transform: translateY(-2px);
            border-color: rgba(6, 182, 212, 0.5);
            box-shadow: 0 8px 25px -5px rgba(6, 182, 212, 0.2);
        }}

        .model-card-btn.active {{
            border-color: #06b6d4;
            background: linear-gradient(145deg, rgba(17, 24, 39, 0.95), rgba(8, 145, 178, 0.2));
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.35), inset 0 0 15px rgba(6, 182, 212, 0.1);
        }}

        .model-card-btn.active.champion {{
            border-color: #10b981;
            background: linear-gradient(145deg, rgba(17, 24, 39, 0.95), rgba(16, 185, 129, 0.2));
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.35), inset 0 0 15px rgba(16, 185, 129, 0.1);
        }}

        /* Custom Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: #0b0f19;
        }}
        ::-webkit-scrollbar-thumb {{
            background: #1f2937;
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: #374151;
        }}

        /* Slider Custom Styling */
        input[type="range"] {{
            accent-color: #06b6d4;
        }}

        /* Badge pulse animation */
        @keyframes pulse-subtle {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.85; transform: scale(1.02); }}
        }}
        .animate-subtle {{
            animation: pulse-subtle 3s infinite ease-in-out;
        }}
    </style>
</head>
<body class="text-gray-100 antialiased selection:bg-cyan-500 selection:text-black">

    <!-- Top Sticky Navigation Bar -->
    <header class="sticky top-0 z-50 bg-[#0b0f19]/80 backdrop-blur-md border-b border-gray-800/80">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                    <svg class="w-5 h-5 text-gray-950 font-bold" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/>
                    </svg>
                </div>
                <div>
                    <div class="flex items-center space-x-2">
                        <span class="text-lg font-bold tracking-tight text-white">HydroFlow</span>
                        <span class="text-xs px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800/80 font-mono font-medium">v2.2-master</span>
                    </div>
                    <p class="text-xs text-gray-400 hidden sm:block">Sentinel-2 12-Band Multispectral Research Benchmark</p>
                </div>
            </div>

            <!-- Desktop Nav Links -->
            <nav class="hidden md:flex items-center space-x-1 text-sm text-gray-300 font-medium">
                <a href="#kpis" class="px-3 py-1.5 rounded-lg hover:text-white hover:bg-gray-800/60 transition">Overview</a>
                <a href="#model-inspector" class="px-3 py-1.5 rounded-lg text-cyan-400 bg-cyan-950/40 border border-cyan-900/40 hover:bg-cyan-900/40 transition">Model Inspector</a>
                <a href="#benchmark-matrix" class="px-3 py-1.5 rounded-lg hover:text-white hover:bg-gray-800/60 transition">Master Matrix</a>
                <a href="#pareto-frontier" class="px-3 py-1.5 rounded-lg hover:text-white hover:bg-gray-800/60 transition">Pareto Frontier</a>
                <a href="#spectral-physics" class="px-3 py-1.5 rounded-lg hover:text-white hover:bg-gray-800/60 transition">Spectral Physics</a>
                <a href="#generative-cfm" class="px-3 py-1.5 rounded-lg hover:text-white hover:bg-gray-800/60 transition">OT-CFM Lab</a>
            </nav>

            <!-- Actions -->
            <div class="flex items-center space-x-2 sm:space-x-3">
                <button onclick="downloadBenchmarkJSON()" class="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-xs font-mono font-medium text-gray-200 border border-gray-700 transition flex items-center space-x-1.5 shadow-sm">
                    <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                    </svg>
                    <span class="hidden sm:inline">Export</span> JSON
                </button>
                <a href="https://github.com/markegyptian55-cloud/HydroFlow-12Channel-Water-Segmentation" target="_blank" rel="noopener noreferrer" class="p-2 rounded-lg bg-gray-800/80 hover:bg-gray-700 text-gray-300 hover:text-white border border-gray-700 transition" title="GitHub Repository">
                    <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
                    </svg>
                </a>
                <!-- Mobile Menu Button -->
                <button onclick="toggleMobileMenu()" class="md:hidden p-2 rounded-lg bg-gray-800 text-gray-300 hover:text-white border border-gray-700" title="Toggle Navigation">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
                    </svg>
                </button>
            </div>
        </div>

        <!-- Collapsible Mobile Menu -->
        <div id="mobile-menu" class="hidden md:hidden px-4 pt-2 pb-4 border-b border-gray-800 bg-[#0b0f19] space-y-1 text-sm font-medium">
            <a href="#kpis" onclick="toggleMobileMenu()" class="block px-3 py-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800/80">Overview</a>
            <a href="#model-inspector" onclick="toggleMobileMenu()" class="block px-3 py-2 rounded-lg text-cyan-400 bg-cyan-950/40 border border-cyan-900/40">Model Inspector</a>
            <a href="#benchmark-matrix" onclick="toggleMobileMenu()" class="block px-3 py-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800/80">Master Matrix</a>
            <a href="#pareto-frontier" onclick="toggleMobileMenu()" class="block px-3 py-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800/80">Pareto Frontier</a>
            <a href="#spectral-physics" onclick="toggleMobileMenu()" class="block px-3 py-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800/80">Spectral Physics</a>
            <a href="#generative-cfm" onclick="toggleMobileMenu()" class="block px-3 py-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800/80">OT-CFM Lab</a>
            <a href="#water-regimes" onclick="toggleMobileMenu()" class="block px-3 py-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800/80">Water Regimes</a>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">

        <!-- Hero Section & Executive KPI Banners -->
        <section id="kpis" class="space-y-6">
            <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-gray-800 pb-6">
                <div>
                    <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800/50 text-cyan-400 text-xs font-medium mb-3">
                        <span class="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
                        <span>Cellula Technologies &bull; Earth Observation Division</span>
                    </div>
                    <h1 class="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                        Multispectral Water Segmentation Benchmark
                    </h1>
                    <p class="text-base text-gray-400 mt-2 max-w-3xl">
                        Comprehensive comparative evaluation of <strong>12-Channel Sentinel-2 U-Net</strong>, ImageNet Transfer Learning (<span class="text-emerald-400">ResNet-34</span> &amp; <span class="text-cyan-400">EfficientNet-B0</span>), Spectral Band Ablation, and Generative Optimal Transport Flow Matching (<span class="text-amber-400">OT-CFM</span>).
                    </p>
                </div>
                <div class="flex items-center space-x-3 text-xs text-gray-400 font-mono bg-gray-900/60 px-3.5 py-2 rounded-xl border border-gray-800">
                    <div><span class="text-gray-500">Pairs:</span> 306</div>
                    <div class="text-gray-700">|</div>
                    <div><span class="text-gray-500">Split:</span> 244 / 62</div>
                    <div class="text-gray-700">|</div>
                    <div><span class="text-gray-500">Pixels:</span> 1.01M</div>
                </div>
            </div>

            <!-- 4 Key Stat Cards -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <!-- Stat 1 -->
                <div class="glass-card p-5 relative overflow-hidden group">
                    <div class="absolute -right-6 -bottom-6 w-24 h-24 bg-emerald-500/10 rounded-full blur-xl group-hover:bg-emerald-500/20 transition"></div>
                    <div class="flex items-center justify-between text-xs text-gray-400 font-medium">
                        <span>PEAK VALIDATION IoU</span>
                        <span class="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px] font-mono">SOTA</span>
                    </div>
                    <div class="text-3xl sm:text-4xl font-black text-emerald-400 mt-2 font-mono tracking-tight">82.10%</div>
                    <div class="text-xs text-gray-400 mt-1 flex items-center space-x-1.5">
                        <span class="text-emerald-400 font-bold">+8.76%</span>
                        <span>vs 12ch Scratch Baseline</span>
                    </div>
                    <div class="mt-3 text-[11px] text-gray-400 border-t border-gray-800 pt-2 font-mono">
                        Model: Pretrained ResNet-34 (12ch)
                    </div>
                </div>

                <!-- Stat 2 -->
                <div class="glass-card p-5 relative overflow-hidden group">
                    <div class="absolute -right-6 -bottom-6 w-24 h-24 bg-cyan-500/10 rounded-full blur-xl group-hover:bg-cyan-500/20 transition"></div>
                    <div class="flex items-center justify-between text-xs text-gray-400 font-medium">
                        <span>EDGE EFFICIENCY FRONTIER</span>
                        <span class="px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 text-[10px] font-mono">6.25M Params</span>
                    </div>
                    <div class="text-3xl sm:text-4xl font-black text-cyan-400 mt-2 font-mono tracking-tight">76.56%</div>
                    <div class="text-xs text-gray-400 mt-1 flex items-center space-x-1.5">
                        <span class="text-cyan-400 font-bold">~4x smaller</span>
                        <span>footprint than ResNet-34</span>
                    </div>
                    <div class="mt-3 text-[11px] text-gray-400 border-t border-gray-800 pt-2 font-mono">
                        Model: Pretrained EfficientNet-B0 (12ch)
                    </div>
                </div>

                <!-- Stat 3 -->
                <div class="glass-card p-5 relative overflow-hidden group">
                    <div class="absolute -right-6 -bottom-6 w-24 h-24 bg-teal-500/10 rounded-full blur-xl group-hover:bg-teal-500/20 transition"></div>
                    <div class="flex items-center justify-between text-xs text-gray-400 font-medium">
                        <span>BANDWIDTH CHAMPION</span>
                        <span class="px-2 py-0.5 rounded bg-teal-950 text-teal-400 border border-teal-800 text-[10px] font-mono">6 Golden Bands</span>
                    </div>
                    <div class="text-3xl sm:text-4xl font-black text-teal-300 mt-2 font-mono tracking-tight">91.83%</div>
                    <div class="text-xs text-gray-400 mt-1 flex items-center space-x-1.5">
                        <span class="text-teal-400 font-bold">Peak Precision</span>
                        <span>(50% less satellite data)</span>
                    </div>
                    <div class="mt-3 text-[11px] text-gray-400 border-t border-gray-800 pt-2 font-mono">
                        Model: Pretrained ResNet-34 (6ch)
                    </div>
                </div>

                <!-- Stat 4 -->
                <div class="glass-card p-5 relative overflow-hidden group">
                    <div class="absolute -right-6 -bottom-6 w-24 h-24 bg-amber-500/10 rounded-full blur-xl group-hover:bg-amber-500/20 transition"></div>
                    <div class="flex items-center justify-between text-xs text-gray-400 font-medium">
                        <span>OT-CFM SYNTHESIS YIELD</span>
                        <span class="px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800 text-[10px] font-mono">48.5% Pass</span>
                    </div>
                    <div class="text-3xl sm:text-4xl font-black text-amber-400 mt-2 font-mono tracking-tight">+3.18%</div>
                    <div class="text-xs text-gray-400 mt-1 flex items-center space-x-1.5">
                        <span class="text-amber-400 font-bold">509 Scenes</span>
                        <span>vetted via Physical Gatekeeper</span>
                    </div>
                    <div class="mt-3 text-[11px] text-gray-400 border-t border-gray-800 pt-2 font-mono">
                        Generative Heun ODE 25-step paths
                    </div>
                </div>
            </div>
        </section>

        <!-- CORE FEATURE: Click-to-Inspect Dynamic Model Curve Inspector -->
        <section id="model-inspector" class="space-y-6 scroll-mt-20">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-gray-800 pb-4">
                <div>
                    <div class="flex items-center space-x-2">
                        <span class="p-1 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                        </span>
                        <h2 class="text-2xl font-bold text-white tracking-tight">Interactive Model &amp; Loss Curve Inspector</h2>
                    </div>
                    <p class="text-sm text-gray-400 mt-1">
                        <strong>Click any model card below</strong> to dynamically load and animate its exact epoch-by-epoch loss trajectories, validation IoU progression, and confusion matrix.
                    </p>
                </div>

                <!-- Overlay Mode Toggle -->
                <div class="flex items-center space-x-3 bg-gray-900/80 px-3.5 py-2 rounded-xl border border-gray-800 self-start md:self-auto">
                    <label class="text-xs text-gray-300 font-medium cursor-pointer flex items-center space-x-2 select-none">
                        <input type="checkbox" id="toggle-overlay-mode" onchange="toggleOverlayMode(this.checked)" class="w-4 h-4 rounded bg-gray-800 border-gray-700 text-cyan-500 focus:ring-0 cursor-pointer">
                        <span>Multi-Model Overlay Mode</span>
                    </label>
                </div>
            </div>

            <!-- Model Selection Cards (7 Models) -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3" id="model-cards-container">
                <!-- Dynamically rendered via JS -->
            </div>

            <!-- Overlay Model Selection Checkboxes (shown when Overlay Mode is ON) -->
            <div id="overlay-selectors" class="hidden p-4 rounded-xl bg-gray-900/90 border border-cyan-900/50 space-y-3">
                <div class="flex items-center justify-between">
                    <div class="text-xs font-semibold text-cyan-400 uppercase tracking-wider">Select Models to Overlay on the Same Canvas:</div>
                    <span class="text-[11px] text-gray-400 font-mono">Compare multiple models simultaneously</span>
                </div>
                <div class="flex flex-wrap gap-2" id="overlay-checkboxes-container">
                    <!-- Populated via JS -->
                </div>
            </div>

            <!-- Inspector Workspace: Canvas & Live Telemetry Sidebar -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                
                <!-- Main Dynamic Chart Container (8 Cols) -->
                <div class="lg:col-span-8 glass-card p-5 sm:p-6 space-y-5">
                    <!-- Chart Metric Tabs & Controls -->
                    <div class="flex flex-wrap items-center justify-between gap-3 border-b border-gray-800 pb-4">
                        <div class="flex items-center space-x-1.5 p-1 bg-gray-900/80 rounded-lg border border-gray-800 text-xs font-medium">
                            <button onclick="switchChartMetric('loss')" id="tab-metric-loss" class="px-3 py-1.5 rounded-md bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 font-semibold transition">
                                Loss Curves (Train vs Val)
                            </button>
                            <button onclick="switchChartMetric('iou')" id="tab-metric-iou" class="px-3 py-1.5 rounded-md text-gray-400 hover:text-gray-200 transition">
                                Validation IoU Progression
                            </button>
                            <button onclick="switchChartMetric('precision_recall')" id="tab-metric-precision-recall" class="px-3 py-1.5 rounded-md text-gray-400 hover:text-gray-200 transition">
                                Precision vs Recall
                            </button>
                        </div>

                        <!-- Telemetry Badge for Active Chart -->
                        <div class="flex items-center space-x-2 text-xs font-mono">
                            <span id="chart-status-pill" class="px-2.5 py-1 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 font-semibold">
                                Inspecting: ResNet-34 12ch
                            </span>
                        </div>
                    </div>

                    <!-- Canvas with Offline SVG Fallback Support -->
                    <div id="chart-canvas-container" class="relative w-full h-[360px] sm:h-[400px]">
                        <canvas id="modelInspectionChart"></canvas>
                        <div id="offline-chart-fallback" class="hidden w-full h-full"></div>
                    </div>

                    <!-- Chart Annotation Footnote -->
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-gray-400 pt-3 border-t border-gray-800 font-mono">
                        <div class="flex flex-wrap items-center gap-3">
                            <span class="flex items-center space-x-1.5">
                                <span class="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block"></span>
                                <span>Train Loss / Precision</span>
                            </span>
                            <span class="flex items-center space-x-1.5">
                                <span class="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block"></span>
                                <span>Val Loss / Recall</span>
                            </span>
                            <span class="flex items-center space-x-1.5">
                                <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block"></span>
                                <span>★ Best Checkpoint</span>
                            </span>
                            <span class="flex items-center space-x-1.5">
                                <span class="w-3 h-0.5 border-t border-dashed border-amber-400 inline-block"></span>
                                <span>Warmup Boundary</span>
                            </span>
                        </div>
                        <div id="chart-warmup-note" class="text-gray-400">
                            Epochs 1-3: Encoder Frozen Warmup &bull; Epochs 4+: Full Fine-Tuning
                        </div>
                    </div>
                </div>

                <!-- Active Model Telemetry & Confusion Matrix Sidebar (4 Cols) -->
                <div class="lg:col-span-4 space-y-4">
                    
                    <!-- Telemetry Card -->
                    <div class="glass-card p-5 space-y-4 border-cyan-900/40">
                        <div class="flex items-start justify-between gap-2 border-b border-gray-800 pb-3">
                            <div>
                                <span id="telemetry-badge" class="px-2 py-0.5 text-[10px] rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-mono uppercase font-bold">
                                    Accuracy Champion
                                </span>
                                <h3 id="telemetry-name" class="text-lg font-bold text-white mt-1">Pretrained ResNet-34 U-Net</h3>
                                <p id="telemetry-arch" class="text-xs text-gray-400 font-mono">SMP U-Net &bull; 12 Bands (Full)</p>
                            </div>
                            <div class="text-right">
                                <span class="text-xs text-gray-400 font-mono block">Params</span>
                                <span id="telemetry-params" class="text-sm font-bold text-cyan-400 font-mono">24.46M</span>
                            </div>
                        </div>

                        <!-- Metrics Grid -->
                        <div class="grid grid-cols-2 gap-3 font-mono">
                            <div class="p-2.5 rounded-lg bg-gray-900/70 border border-gray-800">
                                <div class="text-[10px] text-gray-400 uppercase">Global Pixel IoU</div>
                                <div id="telemetry-iou" class="text-xl font-black text-emerald-400 mt-0.5">81.66%</div>
                                <div id="telemetry-peak-iou" class="text-[10px] text-gray-400">Peak Val: 82.10%</div>
                            </div>
                            <div class="p-2.5 rounded-lg bg-gray-900/70 border border-gray-800">
                                <div class="text-[10px] text-gray-400 uppercase">F1-Score (Dice)</div>
                                <div id="telemetry-f1" class="text-xl font-black text-cyan-400 mt-0.5">89.91%</div>
                                <div class="text-[10px] text-gray-400">Harmonic Mean</div>
                            </div>
                            <div class="p-2.5 rounded-lg bg-gray-900/70 border border-gray-800">
                                <div class="text-[10px] text-gray-400 uppercase">Precision</div>
                                <div id="telemetry-precision" class="text-lg font-bold text-gray-200 mt-0.5">91.48%</div>
                                <div class="text-[10px] text-gray-400">Low False Alarms</div>
                            </div>
                            <div class="p-2.5 rounded-lg bg-gray-900/70 border border-gray-800">
                                <div class="text-[10px] text-gray-400 uppercase">Recall</div>
                                <div id="telemetry-recall" class="text-lg font-bold text-gray-200 mt-0.5">88.39%</div>
                                <div class="text-[10px] text-gray-400">Water Coverage</div>
                            </div>
                        </div>

                        <!-- Run Details -->
                        <div class="space-y-1.5 text-xs border-t border-gray-800 pt-3 text-gray-400 font-mono">
                            <div class="flex justify-between">
                                <span>Training Duration:</span>
                                <span id="telemetry-duration" class="text-gray-200 font-semibold">209.0 s (~2.35 s/epoch)</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Total Epochs Logged:</span>
                                <span id="telemetry-epochs" class="text-gray-200 font-semibold">89 epochs</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Best Checkpoint Saved:</span>
                                <span id="telemetry-best-epoch" class="text-emerald-400 font-semibold">Epoch 29 (Val IoU: 82.10%)</span>
                            </div>
                        </div>
                    </div>

                    <!-- Live Confusion Matrix Widget -->
                    <div class="glass-card p-5 space-y-3">
                        <div class="flex items-center justify-between border-b border-gray-800 pb-2">
                            <h4 class="text-xs font-semibold text-gray-300 uppercase tracking-wider flex items-center space-x-1.5">
                                <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                                <span>Pixel Confusion Matrix</span>
                            </h4>
                            <span class="text-[10px] font-mono text-gray-400">62 Val Scenes &bull; 1,015,808 Pixels</span>
                        </div>

                        <!-- 2x2 Matrix Grid -->
                        <div class="grid grid-cols-2 gap-2 text-xs font-mono">
                            <!-- TP -->
                            <div class="p-2.5 rounded-lg bg-emerald-950/40 border border-emerald-800/60">
                                <div class="text-[10px] text-emerald-400 font-bold uppercase flex justify-between">
                                    <span>True Positive (TP)</span>
                                    <span id="cm-tp-pct">22.1%</span>
                                </div>
                                <div id="cm-tp" class="text-base font-black text-emerald-300 mt-1">225,012</div>
                                <div class="text-[9px] text-gray-400 mt-0.5">Water Correctly Predicted</div>
                            </div>

                            <!-- FP -->
                            <div class="p-2.5 rounded-lg bg-rose-950/40 border border-rose-800/60">
                                <div class="text-[10px] text-rose-400 font-bold uppercase flex justify-between">
                                    <span>False Positive (FP)</span>
                                    <span id="cm-fp-pct">2.1%</span>
                                </div>
                                <div id="cm-fp" class="text-base font-black text-rose-300 mt-1">20,963</div>
                                <div class="text-[9px] text-gray-400 mt-0.5">Land Mistaken for Water</div>
                            </div>

                            <!-- FN -->
                            <div class="p-2.5 rounded-lg bg-amber-950/40 border border-amber-800/60">
                                <div class="text-[10px] text-amber-400 font-bold uppercase flex justify-between">
                                    <span>False Negative (FN)</span>
                                    <span id="cm-fn-pct">2.9%</span>
                                </div>
                                <div id="cm-fn" class="text-base font-black text-amber-300 mt-1">29,568</div>
                                <div class="text-[9px] text-gray-400 mt-0.5">Missed Real Water</div>
                            </div>

                            <!-- TN -->
                            <div class="p-2.5 rounded-lg bg-gray-900/60 border border-gray-800">
                                <div class="text-[10px] text-gray-400 font-bold uppercase flex justify-between">
                                    <span>True Negative (TN)</span>
                                    <span id="cm-tn-pct">72.9%</span>
                                </div>
                                <div id="cm-tn" class="text-base font-black text-gray-300 mt-1">740,265</div>
                                <div class="text-[9px] text-gray-400 mt-0.5">Land Correctly Classified</div>
                            </div>
                        </div>

                        <!-- Progress Bar of Pixel Class Accuracy -->
                        <div class="space-y-1 pt-1">
                            <div class="flex justify-between text-[10px] font-mono text-gray-400">
                                <span>Total Water Detection Accuracy:</span>
                                <span id="cm-water-iou-label" class="text-emerald-400 font-bold">81.66% IoU</span>
                            </div>
                            <div class="w-full bg-gray-800 rounded-full h-2 overflow-hidden flex">
                                <div id="cm-bar-tp" class="bg-emerald-500 h-full" style="width: 88.4%" title="Recall (Captured Water)"></div>
                                <div id="cm-bar-fn" class="bg-amber-500 h-full" style="width: 11.6%" title="FN (Missed Water)"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- SECTION: Master 6-Way Comparative Benchmark & Interactive Table -->
        <section id="benchmark-matrix" class="space-y-6 scroll-mt-20">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-800 pb-4">
                <div>
                    <h2 class="text-2xl font-bold text-white tracking-tight">Official Master Benchmark Matrix</h2>
                    <p class="text-sm text-gray-400 mt-1">
                        Cross-architecture evaluation under identical split (244 train / 62 val) and deterministic seed (42).
                    </p>
                </div>
                
                <!-- Filters -->
                <div class="flex flex-wrap items-center gap-1.5 p-1 bg-gray-900/80 rounded-xl border border-gray-800 text-xs font-medium">
                    <button onclick="filterBenchmarkTable('all')" id="filter-btn-all" class="px-3 py-1.5 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 font-semibold transition">
                        All (7 Models)
                    </button>
                    <button onclick="filterBenchmarkTable('12ch')" id="filter-btn-12ch" class="px-3 py-1.5 rounded-lg text-gray-400 hover:text-white transition">
                        12-Band Full
                    </button>
                    <button onclick="filterBenchmarkTable('6ch')" id="filter-btn-6ch" class="px-3 py-1.5 rounded-lg text-gray-400 hover:text-white transition">
                        6-Band Golden
                    </button>
                    <button onclick="filterBenchmarkTable('transfer')" id="filter-btn-transfer" class="px-3 py-1.5 rounded-lg text-gray-400 hover:text-white transition">
                        Transfer Learning
                    </button>
                    <button onclick="filterBenchmarkTable('scratch')" id="filter-btn-scratch" class="px-3 py-1.5 rounded-lg text-gray-400 hover:text-white transition">
                        Scratch &amp; CFM
                    </button>
                </div>
            </div>

            <!-- Table Card -->
            <div class="glass-card overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs font-mono">
                        <thead class="bg-gray-900/90 text-gray-400 uppercase border-b border-gray-800 text-[11px]">
                            <tr>
                                <th scope="col" class="py-3.5 px-4 font-semibold">Model / Experiment ID</th>
                                <th scope="col" class="py-3.5 px-3 font-semibold">Architecture</th>
                                <th scope="col" class="py-3.5 px-3 font-semibold">Bands</th>
                                <th scope="col" class="py-3.5 px-3 font-semibold text-right">Params</th>
                                <th scope="col" class="py-3.5 px-3 font-semibold text-right text-emerald-400">Global IoU</th>
                                <th scope="col" class="py-3.5 px-3 font-semibold text-right">Precision</th>
                                <th scope="col" class="py-3.5 px-3 font-semibold text-right">Recall</th>
                                <th scope="col" class="py-3.5 px-3 font-semibold text-right text-cyan-400">F1-Score</th>
                                <th scope="col" class="py-3.5 px-3 font-semibold text-right">Duration</th>
                                <th scope="col" class="py-3.5 px-4 text-center">Inspect</th>
                            </tr>
                        </thead>
                        <tbody id="benchmark-table-body" class="divide-y divide-gray-800/80">
                            <!-- Populated via JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- SECTION: Pareto Efficiency Frontier & Metric Multi-Bar Comparison -->
        <section id="pareto-frontier" class="space-y-6 scroll-mt-20">
            <div class="border-b border-gray-800 pb-4">
                <h2 class="text-2xl font-bold text-white tracking-tight">Pareto Efficiency &amp; Metric Comparisons</h2>
                <p class="text-sm text-gray-400 mt-1">
                    Analyzing parameter footprints versus segmentation accuracy frontier, and grouped multi-metric rankings. <strong>Click any point or bar</strong> to inspect that model's exact curves.
                </p>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <!-- Pareto Scatter Plot (7 Cols) -->
                <div class="lg:col-span-7 glass-card p-5 sm:p-6 space-y-4">
                    <div class="flex items-center justify-between border-b border-gray-800 pb-3">
                        <div>
                            <h3 class="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                                <span class="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
                                <span>Pareto Efficiency Frontier (IoU vs Params M)</span>
                            </h3>
                            <p class="text-xs text-gray-400 mt-0.5">Optimal models maximize IoU while minimizing parameter footprint. Click any point to inspect.</p>
                        </div>
                        <span class="px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 text-[10px] font-mono">
                            Interactive Points
                        </span>
                    </div>

                    <div id="pareto-canvas-container" class="relative w-full h-[340px]">
                        <canvas id="paretoScatterChart"></canvas>
                        <div id="offline-pareto-fallback" class="hidden w-full h-full"></div>
                    </div>

                    <!-- Callout explanation -->
                    <div class="p-3.5 rounded-lg bg-gray-900/80 border border-gray-800 text-xs text-gray-300 space-y-1.5 font-sans">
                        <div class="font-semibold text-cyan-300 flex items-center space-x-1.5">
                            <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                            <span>Scientific Pareto Discovery:</span>
                        </div>
                        <p class="text-gray-400 leading-relaxed">
                            <strong>Pretrained EfficientNet-B0 (6.25M)</strong> forms the lightweight Pareto vertex, surpassing the Scratch Baseline (7.77M) by <strong>+3.23% IoU</strong> while being 20% smaller. <strong>ResNet-34 (24.46M)</strong> forms the accuracy apex at <strong>81.66% IoU</strong>, dominating all alternatives.
                        </p>
                    </div>
                </div>

                <!-- Multi-Bar Metric Comparison Chart (5 Cols) -->
                <div class="lg:col-span-5 glass-card p-5 sm:p-6 space-y-4">
                    <div class="flex items-center justify-between border-b border-gray-800 pb-3">
                        <div>
                            <h3 class="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                                <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                                <span>Metric Multi-Bar Rankings</span>
                            </h3>
                            <p class="text-xs text-gray-400 mt-0.5">Comparing Global IoU, Precision, Recall, and F1 across models. Click any bar to inspect.</p>
                        </div>
                    </div>

                    <div id="metrics-canvas-container" class="relative w-full h-[340px]">
                        <canvas id="metricsBarChart"></canvas>
                        <div id="offline-metrics-fallback" class="hidden w-full h-full"></div>
                    </div>

                    <div class="grid grid-cols-2 gap-2 text-[11px] font-mono pt-1 text-gray-400">
                        <div class="flex items-center space-x-1.5"><span class="w-2 h-2 rounded-sm bg-emerald-500"></span><span>Global IoU</span></div>
                        <div class="flex items-center space-x-1.5"><span class="w-2 h-2 rounded-sm bg-cyan-500"></span><span>F1-Score</span></div>
                        <div class="flex items-center space-x-1.5"><span class="w-2 h-2 rounded-sm bg-blue-500"></span><span>Precision</span></div>
                        <div class="flex items-center space-x-1.5"><span class="w-2 h-2 rounded-sm bg-purple-500"></span><span>Recall</span></div>
                    </div>
                </div>
            </div>
        </section>

        <!-- SECTION: Sentinel-2 Remote Sensing Physics & Interactive NDWI Calculator -->
        <section id="spectral-physics" class="space-y-6 scroll-mt-20">
            <div class="border-b border-gray-800 pb-4">
                <div class="flex items-center space-x-2">
                    <span class="p-1 rounded bg-teal-950 text-teal-400 border border-teal-800">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                    </span>
                    <h2 class="text-2xl font-bold text-white tracking-tight">Spectral Physics Studio &amp; NDWI Calculator</h2>
                </div>
                <p class="text-sm text-gray-400 mt-1">
                    Explore the 12 Sentinel-2 MSI spectral bands, water absorption mechanics, and test the real-time NDWI/MNDWI simulator. Click any band chip to highlight its role.
                </p>
            </div>

            <!-- 12-Band Visual Spectrum Explorer -->
            <div class="glass-card p-5 sm:p-6 space-y-4">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-gray-800 pb-3">
                    <h3 class="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                        <span>Sentinel-2 Multispectral Instrument (MSI) 12-Band Architecture</span>
                    </h3>
                    <div class="flex items-center space-x-2 text-xs font-mono">
                        <span class="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                            ★ Golden 6-Band Subset
                        </span>
                        <span class="px-2 py-0.5 rounded bg-gray-900 text-gray-400 border border-gray-800">
                            Discarded (Aerosol / Red-Edge)
                        </span>
                    </div>
                </div>

                <!-- Band Grid Cards -->
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2.5" id="spectral-bands-grid">
                    <!-- Populated via JS -->
                </div>

                <!-- Physical Rationale Card -->
                <div class="p-4 rounded-xl bg-gray-900/80 border border-gray-800 grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-sans">
                    <div class="space-y-1">
                        <div class="font-bold text-emerald-400 flex items-center space-x-1.5">
                            <span>1. Core Absorption Law</span>
                        </div>
                        <p class="text-gray-400 leading-relaxed">
                            Water strongly absorbs in the <strong>Near-Infrared (B8)</strong> and <strong>Short-Wave Infrared (B11, B12)</strong> with reflectance near zero ($R \approx 0$), while terrestrial vegetation strongly reflects ($R \approx 0.5$).
                        </p>
                    </div>
                    <div class="space-y-1">
                        <div class="font-bold text-cyan-400 flex items-center space-x-1.5">
                            <span>2. The 6-Band Golden Subset</span>
                        </div>
                        <p class="text-gray-400 leading-relaxed">
                            Isolating <strong>B2, B3, B4, B8, B11, B12</strong> preserves all essential indices while cutting training time by <strong>37.2%</strong> and reducing satellite downlink volume by <strong>50%</strong>.
                        </p>
                    </div>
                    <div class="space-y-1">
                        <div class="font-bold text-amber-400 flex items-center space-x-1.5">
                            <span>3. Discarded Channels</span>
                        </div>
                        <p class="text-gray-400 leading-relaxed">
                            <strong>B1 &amp; B9</strong> are coarse 60m atmospheric correction bands. <strong>B5, B6, B7</strong> are narrow red-edge transitions that introduce redundant features without improving boundary delineation.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Live NDWI / MNDWI Interactive Simulator -->
            <div id="ndwi-simulator-card" class="glass-card p-5 sm:p-6 space-y-6">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-800 pb-3">
                    <div>
                        <h3 class="text-base font-bold text-white flex items-center space-x-2">
                            <span class="p-1 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>
                            </span>
                            <span>Live Normalized Difference Water Index (NDWI) Simulator</span>
                        </h3>
                        <p class="text-xs text-gray-400 mt-1">
                            Adjust band surface reflectance sliders or choose natural surface presets to see real-time index calculations.
                        </p>
                    </div>

                    <!-- Preset Buttons -->
                    <div class="flex flex-wrap items-center gap-1.5 text-xs font-mono">
                        <span class="text-gray-500 mr-1 text-[11px]">Presets:</span>
                        <button onclick="setNdwiPreset(0.22, 0.02, 0.01)" class="px-2.5 py-1 rounded bg-gray-800 hover:bg-gray-700 text-cyan-300 border border-gray-700 transition">Deep Lake</button>
                        <button onclick="setNdwiPreset(0.35, 0.15, 0.08)" class="px-2.5 py-1 rounded bg-gray-800 hover:bg-gray-700 text-teal-300 border border-gray-700 transition">Turbid River</button>
                        <button onclick="setNdwiPreset(0.08, 0.55, 0.20)" class="px-2.5 py-1 rounded bg-gray-800 hover:bg-gray-700 text-emerald-300 border border-gray-700 transition">Dense Forest</button>
                        <button onclick="setNdwiPreset(0.28, 0.32, 0.38)" class="px-2.5 py-1 rounded bg-gray-800 hover:bg-gray-700 text-yellow-300 border border-gray-700 transition">Dry Soil</button>
                    </div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
                    <!-- Sliders (7 Cols) -->
                    <div class="lg:col-span-7 space-y-4">
                        <!-- Green (B3) -->
                        <div id="container-slider-b3" class="space-y-1.5 p-2 rounded-lg transition">
                            <div class="flex justify-between text-xs font-mono">
                                <span class="text-emerald-400 font-bold">Green Band Reflectance (B3 &bull; 0.560 µm)</span>
                                <span id="val-b3" class="text-white font-bold bg-gray-800 px-2 py-0.5 rounded">0.22</span>
                            </div>
                            <input type="range" id="slider-b3" min="0" max="1" step="0.01" value="0.22" oninput="calculateLiveNdwi()" class="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer">
                        </div>

                        <!-- NIR (B8) -->
                        <div id="container-slider-b8" class="space-y-1.5 p-2 rounded-lg transition">
                            <div class="flex justify-between text-xs font-mono">
                                <span class="text-cyan-400 font-bold">NIR Band Reflectance (B8 &bull; 0.842 µm)</span>
                                <span id="val-b8" class="text-white font-bold bg-gray-800 px-2 py-0.5 rounded">0.02</span>
                            </div>
                            <input type="range" id="slider-b8" min="0" max="1" step="0.01" value="0.02" oninput="calculateLiveNdwi()" class="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer">
                        </div>

                        <!-- SWIR (B11) -->
                        <div id="container-slider-b11" class="space-y-1.5 p-2 rounded-lg transition">
                            <div class="flex justify-between text-xs font-mono">
                                <span class="text-purple-400 font-bold">SWIR-1 Band Reflectance (B11 &bull; 1.610 µm)</span>
                                <span id="val-b11" class="text-white font-bold bg-gray-800 px-2 py-0.5 rounded">0.01</span>
                            </div>
                            <input type="range" id="slider-b11" min="0" max="1" step="0.01" value="0.01" oninput="calculateLiveNdwi()" class="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer">
                        </div>
                    </div>

                    <!-- Calculated Indicators (5 Cols) -->
                    <div class="lg:col-span-5 grid grid-cols-2 gap-3 font-mono">
                        <!-- NDWI Result -->
                        <div class="p-4 rounded-xl bg-gray-900/90 border border-gray-800 space-y-2">
                            <div class="text-[10px] text-gray-400 uppercase">NDWI (McFeeters, 1996)</div>
                            <div class="text-xs text-gray-500 font-serif">(Green - NIR) / (Green + NIR)</div>
                            <div id="ndwi-result-val" class="text-3xl font-black text-cyan-400">+0.833</div>
                            <div id="ndwi-status-badge" class="px-2 py-0.5 rounded text-[10px] bg-cyan-950 text-cyan-300 border border-cyan-800 font-bold inline-block">
                                Water Pixel (&gt; 0.0)
                            </div>
                        </div>

                        <!-- MNDWI Result -->
                        <div class="p-4 rounded-xl bg-gray-900/90 border border-gray-800 space-y-2">
                            <div class="text-[10px] text-gray-400 uppercase">MNDWI (Xu, 2006)</div>
                            <div class="text-xs text-gray-500 font-serif">(Green - SWIR) / (Green + SWIR)</div>
                            <div id="mndwi-result-val" class="text-3xl font-black text-emerald-400">+0.913</div>
                            <div id="mndwi-status-badge" class="px-2 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-800 font-bold inline-block">
                                Clear Water Body
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- SECTION: Optimal Transport Flow Matching (OT-CFM) Generative Lab -->
        <section id="generative-cfm" class="space-y-6 scroll-mt-20">
            <div class="border-b border-gray-800 pb-4">
                <div class="flex items-center space-x-2">
                    <span class="p-1 rounded bg-amber-950 text-amber-400 border border-amber-800">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/></svg>
                    </span>
                    <h2 class="text-2xl font-bold text-white tracking-tight">Optimal Transport Flow Matching (OT-CFM) Lab</h2>
                </div>
                <p class="text-sm text-gray-400 mt-1">
                    Generating multispectral satellite scenes along straight probability trajectories with automated 3-Stage Physical Gatekeeper vetting.
                </p>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <!-- ODE Probability Path Visualizer (6 Cols) -->
                <div class="lg:col-span-6 glass-card p-5 sm:p-6 space-y-4">
                    <div class="flex items-center justify-between border-b border-gray-800 pb-3">
                        <h3 class="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                            <span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                            <span>Straight-Path Probability Flow: $x_t = (1-t)x_0 + t x_1$</span>
                        </h3>
                        <span class="text-xs text-amber-400 font-mono">25 Heun Steps</span>
                    </div>

                    <!-- Flow Diagram -->
                    <div class="p-4 rounded-xl bg-gray-900/90 border border-gray-800 space-y-4 text-xs font-mono">
                        <div class="flex items-center justify-between text-gray-400">
                            <div class="text-center p-3 rounded-lg bg-gray-800/80 border border-gray-700 w-28">
                                <div class="text-[10px] text-gray-400 font-bold">t = 0.0</div>
                                <div class="text-xs text-cyan-300 font-bold mt-1">Gaussian Noise</div>
                                <div class="text-[10px] text-gray-400 mt-0.5">N(0, I) [6, 128, 128]</div>
                            </div>
                            <div class="flex-1 px-3 text-center">
                                <div class="text-amber-400 font-bold text-[11px]">&rarr; dx/dt = v_&theta;(x_t, t, c) &rarr;</div>
                                <div class="text-[10px] text-gray-400 mt-1">2nd-Order Heun Predictor-Corrector</div>
                                <div class="w-full bg-gray-800 rounded-full h-1.5 mt-2 overflow-hidden">
                                    <div class="bg-gradient-to-r from-cyan-500 via-amber-500 to-emerald-500 h-full w-full"></div>
                                </div>
                            </div>
                            <div class="text-center p-3 rounded-lg bg-emerald-950/60 border border-emerald-800 w-28">
                                <div class="text-[10px] text-emerald-400 font-bold">t = 1.0</div>
                                <div class="text-xs text-emerald-300 font-bold mt-1">Sentinel-2 Scene</div>
                                <div class="text-[10px] text-gray-400 mt-0.5">Synthetic Multispectral</div>
                            </div>
                        </div>

                        <!-- Math callout -->
                        <div class="p-3 rounded-lg bg-black/40 border border-gray-800 text-[11px] text-gray-300 space-y-1">
                            <div class="text-amber-300 font-bold">Continuous Normalizing Flow vs Curved Diffusion:</div>
                            <p class="text-gray-400 font-sans leading-relaxed">
                                Standard DDPM diffusion requires 1,000 curved steps. Optimal Transport CFM solves straight vector fields in <strong>25 Heun steps</strong> without score approximation drift, generating 1,050 candidates in 312 seconds on Kaggle T4 GPU.
                            </p>
                        </div>
                    </div>
                </div>

                <!-- 3-Stage Gatekeeper Rejection Funnel (6 Cols) -->
                <div class="lg:col-span-6 glass-card p-5 sm:p-6 space-y-4">
                    <div class="flex items-center justify-between border-b border-gray-800 pb-3">
                        <h3 class="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                            <span>3-Stage Physical Quality Gatekeeper Funnel</span>
                        </h3>
                        <span class="text-xs text-emerald-400 font-mono">48.5% Acceptance</span>
                    </div>

                    <!-- Funnel Stages -->
                    <div class="space-y-2.5 font-mono text-xs">
                        <!-- Total Candidates -->
                        <div class="p-2.5 rounded-lg bg-gray-900 border border-gray-800 flex items-center justify-between">
                            <span class="text-gray-300">Generated Candidate Scenes:</span>
                            <span class="font-bold text-white">1,050 scenes (7 seeds)</span>
                        </div>

                        <!-- Stage 1 -->
                        <div class="p-2.5 rounded-lg bg-rose-950/30 border border-rose-900/50 flex items-center justify-between">
                            <div>
                                <span class="text-rose-400 font-bold">Stage 1: Variance Filter (&sigma; &lt; 0.025)</span>
                                <div class="text-[10px] text-gray-400">Rejects degenerate flat/solid generations</div>
                            </div>
                            <div class="text-right">
                                <span class="text-rose-400 font-bold">-280 rejected</span>
                                <div class="text-[10px] text-gray-400">770 remaining</div>
                            </div>
                        </div>

                        <!-- Stage 2 -->
                        <div class="p-2.5 rounded-lg bg-amber-950/30 border border-amber-900/50 flex items-center justify-between">
                            <div>
                                <span class="text-amber-400 font-bold">Stage 2: Physical NIR Absorption (&Delta;_NIR &ge; 0.015)</span>
                                <div class="text-[10px] text-gray-400">Enforces physical law: water must absorb NIR</div>
                            </div>
                            <div class="text-right">
                                <span class="text-amber-400 font-bold">-140 rejected</span>
                                <div class="text-[10px] text-gray-400">630 remaining</div>
                            </div>
                        </div>

                        <!-- Stage 3 -->
                        <div class="p-2.5 rounded-lg bg-indigo-950/30 border border-indigo-900/50 flex items-center justify-between">
                            <div>
                                <span class="text-indigo-400 font-bold">Stage 3: Spatial Alignment (IoU &ge; 0.15)</span>
                                <div class="text-[10px] text-gray-400">Enforces structural overlap with conditioning mask</div>
                            </div>
                            <div class="text-right">
                                <span class="text-indigo-400 font-bold">-121 rejected</span>
                                <div class="text-[10px] text-gray-400">509 passed</div>
                            </div>
                        </div>

                        <!-- Final Accepted -->
                        <div class="p-3 rounded-lg bg-emerald-950/50 border border-emerald-800 flex items-center justify-between">
                            <div>
                                <span class="text-emerald-300 font-bold text-sm">Accepted High-Fidelity Dataset:</span>
                                <div class="text-[10px] text-gray-400 font-sans">Scaled Training Pipeline: 244 real &rarr; 753 total scenes (+208.6%)</div>
                            </div>
                            <div class="text-right">
                                <span class="text-emerald-400 font-black text-lg">509 Scenes</span>
                                <div class="text-[10px] text-emerald-400 font-bold">+3.18% IoU Boost</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- SECTION: Water Regimes Qualitative Error Breakdown -->
        <section id="water-regimes" class="space-y-6 scroll-mt-20">
            <div class="border-b border-gray-800 pb-4">
                <h2 class="text-2xl font-bold text-white tracking-tight">Qualitative Water Regimes &amp; Spatial Error Breakdown</h2>
                <p class="text-sm text-gray-400 mt-1">
                    Performance profiling across hydrological environments and physical spatial downsampling constraints.
                </p>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <!-- Regime 1 -->
                <div class="glass-card p-5 space-y-3">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-mono font-bold text-emerald-400">REGIME 1</span>
                        <span class="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px] font-mono">99.8% Prec</span>
                    </div>
                    <h3 class="text-base font-bold text-white">Open Ocean &amp; Deep Lakes</h3>
                    <p class="text-xs text-gray-400 leading-relaxed font-sans">
                        Uniform water surfaces with pronounced NIR absorption. ResNet-34 achieves zero false alarms and 99.8% precision across expansive bodies.
                    </p>
                    <div class="text-[11px] font-mono text-emerald-400 border-t border-gray-800 pt-2">
                        Status: Fully Mastered
                    </div>
                </div>

                <!-- Regime 2 -->
                <div class="glass-card p-5 space-y-3">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-mono font-bold text-cyan-400">REGIME 2</span>
                        <span class="px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 text-[10px] font-mono">91.8% Prec</span>
                    </div>
                    <h3 class="text-base font-bold text-white">Meandering Rivers &amp; Coastlines</h3>
                    <p class="text-xs text-gray-400 leading-relaxed font-sans">
                        Curvilinear shorelines. The skip connections in U-Net successfully preserve high-frequency edge gradients along complex coastal sandbars.
                    </p>
                    <div class="text-[11px] font-mono text-cyan-400 border-t border-gray-800 pt-2">
                        Status: Sharp Delineation
                    </div>
                </div>

                <!-- Regime 3 -->
                <div class="glass-card p-5 space-y-3">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-mono font-bold text-amber-400">REGIME 3</span>
                        <span class="px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800 text-[10px] font-mono">Challenging</span>
                    </div>
                    <h3 class="text-base font-bold text-white">Narrow Streams (&le; 2 Pixels)</h3>
                    <p class="text-xs text-gray-400 leading-relaxed font-sans">
                        The <strong>32x encoder bottleneck</strong> ($128 \rightarrow 4$ px) compresses thin streams to sub-pixel latent dimensions, causing occasional stream fragmentation.
                    </p>
                    <div class="text-[11px] font-mono text-amber-400 border-t border-gray-800 pt-2">
                        Physical Bottleneck Identified
                    </div>
                </div>

                <!-- Regime 4 -->
                <div class="glass-card p-5 space-y-3">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-mono font-bold text-purple-400">REGIME 4</span>
                        <span class="px-2 py-0.5 rounded bg-purple-950 text-purple-400 border border-purple-800 text-[10px] font-mono">MNDWI Key</span>
                    </div>
                    <h3 class="text-base font-bold text-white">Turbid Waters &amp; Wetlands</h3>
                    <p class="text-xs text-gray-400 leading-relaxed font-sans">
                        Suspended sediments elevate green and red reflectance. Inclusion of <strong>SWIR-1 (B11)</strong> is mathematically required to avoid false vegetation classification.
                    </p>
                    <div class="text-[11px] font-mono text-purple-400 border-t border-gray-800 pt-2">
                        Solved via SWIR-1 (B11)
                    </div>
                </div>
            </div>
        </section>

        <!-- Engineering Footer & Citation -->
        <footer class="border-t border-gray-800/80 pt-8 pb-12 text-xs text-gray-400 font-mono space-y-4">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                    <span class="text-gray-200 font-bold">HydroFlow Research Benchmark</span> &bull; Author: Mohamed Mostafa Elbasyouni
                    <div class="text-gray-500 text-[11px]">Cellula Technologies &bull; Earth Observation &amp; Applied Computer Vision</div>
                </div>
                <div class="flex items-center space-x-3">
                    <button onclick="copyBibtexCitation()" class="px-2.5 py-1 rounded bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 transition">
                        Copy BibTeX
                    </button>
                    <a href="https://github.com/markegyptian55-cloud/HydroFlow-12Channel-Water-Segmentation" target="_blank" rel="noopener noreferrer" class="text-cyan-400 hover:underline">
                        GitHub Repo
                    </a>
                </div>
            </div>
            <div class="text-gray-500 text-[10px] leading-relaxed">
                Evaluated on 306 Sentinel-2 scenes under deterministic seed 42. Metrics adhere strictly to the Master 6-Way Comparative Matrix. Standalone execution: 100% self-contained single HTML artifact.
            </div>
        </footer>

    </main>

    <!-- Embedded Structured Dataset -->
    <script>
        const BENCHMARK_DATA = {data_json_str};
    </script>

    <!-- Application Controller Logic -->
    <script>
        // State Store
        let activeModelId = 'W2-Pretrained-ResNet34-12ch';
        let activeChartMetric = 'loss'; // 'loss' | 'iou' | 'precision_recall'
        let isOverlayMode = false;
        let overlaySelectedModels = ['W2-Pretrained-ResNet34-12ch', 'W2-Pretrained-EffNetB0-12ch', 'W1-Scratch-12ch'];
        let activeTableFilter = 'all';

        // Chart References
        let modelInspectionChart = null;
        let paretoScatterChart = null;
        let metricsBarChart = null;

        // Custom Chart.js Inline Plugin for Warmup Phase & Best Checkpoint Canvas Highlights
        const inspectionAnnotationsPlugin = {{
            id: 'inspectionAnnotations',
            afterDraw: (chart) => {{
                if (isOverlayMode) return;
                const activeModel = BENCHMARK_DATA.models.find(m => m.id === activeModelId);
                if (!activeModel) return;

                const xScale = chart.scales.x;
                const yScale = chart.scales.y;
                if (!xScale || !yScale) return;
                const ctx = chart.ctx;

                // 1. Warmup Boundary Highlight (if warmup_epochs > 0)
                const warmupEpoch = activeModel.warmup_epochs;
                if (warmupEpoch && warmupEpoch > 0) {{
                    const xWarmup = xScale.getPixelForValue(warmupEpoch);
                    if (xWarmup >= xScale.left && xWarmup <= xScale.right) {{
                        ctx.save();
                        // Shaded warmup background
                        ctx.fillStyle = 'rgba(251, 191, 36, 0.05)';
                        ctx.fillRect(xScale.left, yScale.top, xWarmup - xScale.left, yScale.bottom - yScale.top);

                        // Vertical dashed amber line
                        ctx.strokeStyle = '#f59e0b';
                        ctx.lineWidth = 1.5;
                        ctx.setLineDash([4, 4]);
                        ctx.beginPath();
                        ctx.moveTo(xWarmup, yScale.top);
                        ctx.lineTo(xWarmup, yScale.bottom);
                        ctx.stroke();

                        // Warmup tags
                        ctx.fillStyle = '#f59e0b';
                        ctx.font = '10px "JetBrains Mono", monospace';
                        ctx.textAlign = 'right';
                        ctx.fillText(`Warmup End (Ep ${{warmupEpoch}})`, xWarmup - 6, yScale.top + 16);

                        ctx.fillStyle = '#10b981';
                        ctx.textAlign = 'left';
                        ctx.fillText(`Fine-Tuning →`, xWarmup + 6, yScale.top + 16);
                        ctx.restore();
                    }}
                }}

                // 2. Best Checkpoint Marker
                const bestEpoch = activeModel.best_epoch;
                if (bestEpoch && bestEpoch > 0) {{
                    const xBest = xScale.getPixelForValue(bestEpoch);
                    if (xBest >= xScale.left && xBest <= xScale.right) {{
                        ctx.save();
                        ctx.strokeStyle = 'rgba(16, 185, 129, 0.45)';
                        ctx.lineWidth = 1.2;
                        ctx.setLineDash([2, 2]);
                        ctx.beginPath();
                        ctx.moveTo(xBest, yScale.top);
                        ctx.lineTo(xBest, yScale.bottom);
                        ctx.stroke();

                        ctx.fillStyle = '#10b981';
                        ctx.font = 'bold 9px "JetBrains Mono", monospace';
                        ctx.textAlign = 'center';
                        ctx.fillText(`★ Best (Ep ${{bestEpoch}})`, xBest, yScale.top + 32);
                        ctx.restore();
                    }}
                }}
            }}
        }};

        // Initialization
        document.addEventListener('DOMContentLoaded', () => {{
            renderModelCards();
            renderOverlayCheckboxes();
            renderBenchmarkTable();
            renderSpectralBands();
            calculateLiveNdwi();
            initInspectionChart();
            initParetoScatterChart();
            initMetricsBarChart();
            updateModelTelemetry(activeModelId);
        }});

        // Mobile Menu Toggle
        function toggleMobileMenu() {{
            const menu = document.getElementById('mobile-menu');
            if (menu) menu.classList.toggle('hidden');
        }}

        // Render Model Selector Cards
        function renderModelCards() {{
            const container = document.getElementById('model-cards-container');
            if (!container) return;
            container.innerHTML = '';

            BENCHMARK_DATA.models.forEach((m) => {{
                const isChampion = m.is_champion;
                const isActive = m.id === activeModelId;
                const card = document.createElement('div');
                card.className = `model-card-btn glass-card p-4 rounded-xl flex flex-col justify-between ${{isActive ? (isChampion ? 'active champion' : 'active') : ''}}`;
                card.id = `card-${{m.id}}`;
                card.onclick = () => selectModel(m.id);

                card.innerHTML = `
                    <div>
                        <div class="flex items-center justify-between text-[10px] font-mono mb-2">
                            <span class="px-2 py-0.5 rounded ${{m.bands === 12 ? 'bg-cyan-950 text-cyan-400 border border-cyan-800' : 'bg-teal-950 text-teal-400 border border-teal-800'}}">
                                ${{m.band_type}}
                            </span>
                            <span class="px-2 py-0.5 rounded ${{isChampion ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-gray-800 text-gray-400'}} font-bold">
                                ${{m.badge}}
                            </span>
                        </div>
                        <h4 class="text-sm font-bold text-white tracking-tight">${{m.short_name}}</h4>
                        <div class="text-[11px] text-gray-400 font-mono mt-0.5">${{m.architecture}}</div>
                    </div>

                    <div class="mt-4 pt-3 border-t border-gray-800/80 flex items-end justify-between font-mono">
                        <div>
                            <span class="text-[10px] text-gray-400 block uppercase">Global IoU</span>
                            <span class="text-xl font-black text-emerald-400">${{m.global_iou.toFixed(2)}}%</span>
                        </div>
                        <div class="text-right">
                            <span class="text-[10px] text-gray-400 block uppercase">Params</span>
                            <span class="text-xs font-bold text-gray-300">${{m.params_m}}M</span>
                        </div>
                    </div>
                `;
                container.appendChild(card);
            }});
        }}

        // Select a Model
        function selectModel(modelId) {{
            activeModelId = modelId;
            
            // In overlay mode, also ensure this model is included in the overlay selection
            if (isOverlayMode) {{
                if (!overlaySelectedModels.includes(modelId)) {{
                    overlaySelectedModels.push(modelId);
                }}
                const cb = document.querySelector(`#overlay-checkboxes-container input[value="${{modelId}}"]`);
                if (cb) cb.checked = true;
            }}

            // Update Card CSS classes
            BENCHMARK_DATA.models.forEach(m => {{
                const el = document.getElementById(`card-${{m.id}}`);
                if (el) {{
                    el.classList.remove('active', 'champion');
                    if (m.id === activeModelId) {{
                        el.classList.add('active');
                        if (m.is_champion) el.classList.add('champion');
                    }}
                }}
            }});

            updateModelTelemetry(modelId);
            updateInspectionChart();
        }}

        // Update Telemetry & Confusion Matrix Sidebar
        function updateModelTelemetry(modelId) {{
            const model = BENCHMARK_DATA.models.find(m => m.id === modelId);
            if (!model) return;

            document.getElementById('telemetry-name').innerText = model.name;
            document.getElementById('telemetry-arch').innerText = `${{model.architecture}} • ${{model.band_type}} • ${{model.backbone}}`;
            document.getElementById('telemetry-badge').innerText = model.badge;
            document.getElementById('telemetry-badge').className = `px-2 py-0.5 text-[10px] rounded ${{model.is_champion ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-cyan-950 text-cyan-400 border border-cyan-800'}} font-mono uppercase font-bold`;
            document.getElementById('telemetry-params').innerText = `${{model.params_m}}M`;
            document.getElementById('telemetry-iou').innerText = `${{model.global_iou.toFixed(2)}}%`;
            document.getElementById('telemetry-peak-iou').innerText = `Peak Val: ${{model.peak_val_iou.toFixed(2)}}%`;
            document.getElementById('telemetry-f1').innerText = `${{model.f1_score.toFixed(2)}}%`;
            document.getElementById('telemetry-precision').innerText = `${{model.precision.toFixed(2)}}%`;
            document.getElementById('telemetry-recall').innerText = `${{model.recall.toFixed(2)}}%`;

            const sPerEpoch = (model.duration_s / model.total_epochs).toFixed(2);
            document.getElementById('telemetry-duration').innerText = `${{model.duration_s.toFixed(1)}} s (~${{sPerEpoch}} s/epoch)`;
            document.getElementById('telemetry-epochs').innerText = `${{model.total_epochs}} epochs logged`;
            document.getElementById('telemetry-best-epoch').innerText = `Epoch ${{model.best_epoch}} (Val IoU: ${{model.peak_val_iou.toFixed(2)}}%)`;

            document.getElementById('chart-status-pill').innerText = `Inspecting: ${{model.short_name}}`;

            // Confusion Matrix
            const cm = model.confusion_matrix;
            document.getElementById('cm-tp').innerText = Number(cm.tp).toLocaleString();
            document.getElementById('cm-fp').innerText = Number(cm.fp).toLocaleString();
            document.getElementById('cm-fn').innerText = Number(cm.fn).toLocaleString();
            document.getElementById('cm-tn').innerText = Number(cm.tn).toLocaleString();

            const total = cm.total || 1015808;
            document.getElementById('cm-tp-pct').innerText = `${{((cm.tp / total) * 100).toFixed(1)}}%`;
            document.getElementById('cm-fp-pct').innerText = `${{((cm.fp / total) * 100).toFixed(1)}}%`;
            document.getElementById('cm-fn-pct').innerText = `${{((cm.fn / total) * 100).toFixed(1)}}%`;
            document.getElementById('cm-tn-pct').innerText = `${{((cm.tn / total) * 100).toFixed(1)}}%`;

            const waterRecall = (cm.tp / (cm.tp + cm.fn)) * 100;
            document.getElementById('cm-bar-tp').style.width = `${{waterRecall}}%`;
            document.getElementById('cm-bar-fn').style.width = `${{100 - waterRecall}}%`;
            document.getElementById('cm-water-iou-label').innerText = `${{model.global_iou.toFixed(2)}}% IoU`;

            // Warmup note
            const warmupNote = document.getElementById('chart-warmup-note');
            if (model.warmup_epochs > 0) {{
                warmupNote.innerText = `Epochs 1-${{model.warmup_epochs}}: Encoder Frozen Warmup • Epochs ${{model.warmup_epochs + 1}}+: Cosine Annealing Fine-Tuning`;
            }} else {{
                warmupNote.innerText = `Trained from Scratch across all ${{model.total_epochs}} epochs (no frozen warmup phase)`;
            }}
        }}

        // Metric Tabs for Chart
        function switchChartMetric(metric) {{
            activeChartMetric = metric;

            ['loss', 'iou', 'precision_recall'].forEach(m => {{
                const btn = document.getElementById(`tab-metric-${{m.replace('_', '-')}}`);
                if (btn) {{
                    if (m === metric) {{
                        btn.className = 'px-3 py-1.5 rounded-md bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 font-semibold transition';
                    }} else {{
                        btn.className = 'px-3 py-1.5 rounded-md text-gray-400 hover:text-gray-200 transition';
                    }}
                }}
            }});

            updateInspectionChart();
        }}

        // Overlay Mode Toggle
        function toggleOverlayMode(enabled) {{
            isOverlayMode = enabled;
            const container = document.getElementById('overlay-selectors');
            if (enabled) {{
                container.classList.remove('hidden');
                if (!overlaySelectedModels.includes(activeModelId)) {{
                    overlaySelectedModels.push(activeModelId);
                    const cb = document.querySelector(`#overlay-checkboxes-container input[value="${{activeModelId}}"]`);
                    if (cb) cb.checked = true;
                }}
            }} else {{
                container.classList.add('hidden');
            }}
            updateInspectionChart();
        }}

        function renderOverlayCheckboxes() {{
            const container = document.getElementById('overlay-checkboxes-container');
            if (!container) return;
            container.innerHTML = '';

            BENCHMARK_DATA.models.forEach(m => {{
                const isChecked = overlaySelectedModels.includes(m.id);
                const label = document.createElement('label');
                label.className = 'flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-gray-800 text-xs font-mono cursor-pointer hover:bg-gray-700 border border-gray-700 select-none';
                label.innerHTML = `
                    <input type="checkbox" value="${{m.id}}" ${{isChecked ? 'checked' : ''}} onchange="updateOverlaySelection('${{m.id}}', this.checked)" class="rounded bg-gray-900 border-gray-700 text-cyan-500 focus:ring-0 cursor-pointer">
                    <span style="color: ${{m.color}}">${{m.short_name}}</span>
                `;
                container.appendChild(label);
            }});
        }}

        function updateOverlaySelection(modelId, isChecked) {{
            if (isChecked) {{
                if (!overlaySelectedModels.includes(modelId)) overlaySelectedModels.push(modelId);
            }} else {{
                overlaySelectedModels = overlaySelectedModels.filter(id => id !== modelId);
            }}
            // Prevent completely empty overlay selection
            if (overlaySelectedModels.length === 0) {{
                overlaySelectedModels = [activeModelId];
                const cb = document.querySelector(`#overlay-checkboxes-container input[value="${{activeModelId}}"]`);
                if (cb) cb.checked = true;
            }}
            updateInspectionChart();
        }}

        // Initialize Dynamic Inspection Chart
        function initInspectionChart() {{
            const canvas = document.getElementById('modelInspectionChart');
            if (!canvas) return;

            if (typeof Chart === 'undefined') {{
                renderOfflineSvgCurve();
                return;
            }}

            const ctx = canvas.getContext('2d');
            modelInspectionChart = new Chart(ctx, {{
                type: 'line',
                data: {{ datasets: [] }},
                plugins: [inspectionAnnotationsPlugin],
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        mode: 'nearest',
                        intersect: false,
                    }},
                    plugins: {{
                        legend: {{
                            labels: {{
                                color: '#9ca3af',
                                font: {{ family: 'JetBrains Mono', size: 11 }}
                            }}
                        }},
                        tooltip: {{
                            backgroundColor: 'rgba(15, 23, 42, 0.95)',
                            titleColor: '#f3f4f6',
                            bodyColor: '#e2e8f0',
                            borderColor: 'rgba(255, 255, 255, 0.1)',
                            borderWidth: 1,
                            padding: 10,
                            titleFont: {{ family: 'JetBrains Mono', size: 12 }},
                            bodyFont: {{ family: 'JetBrains Mono', size: 11 }},
                            callbacks: {{
                                title: (items) => {{
                                    if (items.length > 0 && items[0].parsed && items[0].parsed.x !== undefined) {{
                                        return `Epoch ${{items[0].parsed.x}}`;
                                    }}
                                    return '';
                                }},
                                label: (item) => {{
                                    const lbl = item.dataset.label || '';
                                    const val = item.parsed && item.parsed.y !== undefined ? Number(item.parsed.y).toFixed(4) : '';
                                    return ` ${{lbl}}: ${{val}}`;
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            type: 'linear',
                            min: 1,
                            grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                            ticks: {{ color: '#9ca3af', font: {{ family: 'JetBrains Mono', size: 10 }} }},
                            title: {{ display: true, text: 'Epoch Number', color: '#6b7280' }}
                        }},
                        y: {{
                            grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                            ticks: {{ color: '#9ca3af', font: {{ family: 'JetBrains Mono', size: 10 }} }}
                        }}
                    }}
                }}
            }});

            updateInspectionChart();
        }}

        // Update Inspection Chart with Selected Model or Overlay
        function updateInspectionChart() {{
            if (typeof Chart === 'undefined') {{
                renderOfflineSvgCurve();
                return;
            }}
            if (!modelInspectionChart) return;

            if (isOverlayMode) {{
                renderOverlayChart();
            }} else {{
                renderSingleModelChart();
            }}
        }}

        function renderSingleModelChart() {{
            const model = BENCHMARK_DATA.models.find(m => m.id === activeModelId);
            if (!model || !model.epochs || model.epochs.length === 0) return;

            const epochs = model.epochs;
            const datasets = [];

            // Point styling to highlight best checkpoint
            const pointRadiusLoss = epochs.map(e => e.epoch === model.best_epoch ? 6 : (epochs.length > 50 ? 0 : 2));
            const pointColorsLoss = epochs.map(e => e.epoch === model.best_epoch ? '#10b981' : '#fbbf24');
            const pointBordersLoss = epochs.map(e => e.epoch === model.best_epoch ? '#ffffff' : '#fbbf24');

            const pointRadiusIoU = epochs.map(e => e.epoch === model.best_epoch ? 7 : (epochs.length > 50 ? 0 : 2.5));
            const pointColorsIoU = epochs.map(e => e.epoch === model.best_epoch ? '#10b981' : '#34d399');
            const pointBordersIoU = epochs.map(e => e.epoch === model.best_epoch ? '#ffffff' : '#34d399');

            if (activeChartMetric === 'loss') {{
                datasets.push({{
                    label: `${{model.short_name}} Train Loss`,
                    data: epochs.map(e => ({{ x: e.epoch, y: e.train_loss }})),
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.08)',
                    borderWidth: 2.2,
                    fill: true,
                    tension: 0.25,
                    pointRadius: epochs.length > 50 ? 0 : 2,
                    pointHoverRadius: 5
                }});
                datasets.push({{
                    label: `${{model.short_name}} Val Loss`,
                    data: epochs.map(e => ({{ x: e.epoch, y: e.val_loss }})),
                    borderColor: '#fbbf24',
                    backgroundColor: 'rgba(251, 191, 36, 0.08)',
                    borderWidth: 2.2,
                    fill: true,
                    tension: 0.25,
                    pointRadius: pointRadiusLoss,
                    pointBackgroundColor: pointColorsLoss,
                    pointBorderColor: pointBordersLoss,
                    pointBorderWidth: 1.5,
                    pointHoverRadius: 6
                }});
            }} else if (activeChartMetric === 'iou') {{
                datasets.push({{
                    label: `${{model.short_name}} Val IoU (%)`,
                    data: epochs.map(e => ({{ x: e.epoch, y: +(e.val_iou * 100).toFixed(2) }})),
                    borderColor: '#34d399',
                    backgroundColor: 'rgba(52, 211, 153, 0.12)',
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.25,
                    pointRadius: pointRadiusIoU,
                    pointBackgroundColor: pointColorsIoU,
                    pointBorderColor: pointBordersIoU,
                    pointBorderWidth: 2,
                    pointHoverRadius: 7
                }});
            }} else if (activeChartMetric === 'precision_recall') {{
                datasets.push({{
                    label: 'Precision (%)',
                    data: epochs.map(e => ({{ x: e.epoch, y: +(e.precision * 100).toFixed(2) }})),
                    borderColor: '#22d3ee',
                    borderWidth: 2,
                    tension: 0.25,
                    pointRadius: 0
                }});
                datasets.push({{
                    label: 'Recall (%)',
                    data: epochs.map(e => ({{ x: e.epoch, y: +(e.recall * 100).toFixed(2) }})),
                    borderColor: '#e879f9',
                    borderWidth: 2,
                    tension: 0.25,
                    pointRadius: 0
                }});
                datasets.push({{
                    label: 'F1-Score (%)',
                    data: epochs.map(e => ({{ x: e.epoch, y: +(e.f1 * 100).toFixed(2) }})),
                    borderColor: '#10b981',
                    borderWidth: 2,
                    tension: 0.25,
                    pointRadius: 0
                }});
            }}

            modelInspectionChart.data.datasets = datasets;
            modelInspectionChart.options.scales.x.max = Math.max(...epochs.map(e => e.epoch));
            modelInspectionChart.options.scales.y.title = {{
                display: true,
                text: activeChartMetric === 'loss' ? 'Loss Magnitude (BCE + Dice)' : 'Percentage (%)',
                color: '#6b7280'
            }};
            modelInspectionChart.update();
        }}

        function renderOverlayChart() {{
            const selected = BENCHMARK_DATA.models.filter(m => overlaySelectedModels.includes(m.id));
            if (selected.length === 0) return;

            let maxEpoch = 0;
            const datasets = [];

            selected.forEach(m => {{
                if (!m.epochs || m.epochs.length === 0) return;
                const mMax = Math.max(...m.epochs.map(e => e.epoch));
                if (mMax > maxEpoch) maxEpoch = mMax;

                if (activeChartMetric === 'loss') {{
                    datasets.push({{
                        label: `${{m.short_name}} Val Loss`,
                        data: m.epochs.map(e => ({{ x: e.epoch, y: e.val_loss }})),
                        borderColor: m.color,
                        borderWidth: 2.2,
                        tension: 0.25,
                        pointRadius: 0
                    }});
                }} else if (activeChartMetric === 'iou') {{
                    datasets.push({{
                        label: `${{m.short_name}} Val IoU (%)`,
                        data: m.epochs.map(e => ({{ x: e.epoch, y: +(e.val_iou * 100).toFixed(2) }})),
                        borderColor: m.color,
                        borderWidth: 2.4,
                        tension: 0.25,
                        pointRadius: 0
                    }});
                }} else {{
                    // Precision vs Recall in Overlay Mode: Plot both solid Precision and dashed Recall
                    datasets.push({{
                        label: `${{m.short_name}} Prec (%)`,
                        data: m.epochs.map(e => ({{ x: e.epoch, y: +(e.precision * 100).toFixed(2) }})),
                        borderColor: m.color,
                        borderWidth: 2.2,
                        tension: 0.25,
                        pointRadius: 0
                    }});
                    datasets.push({{
                        label: `${{m.short_name}} Rec (%)`,
                        data: m.epochs.map(e => ({{ x: e.epoch, y: +(e.recall * 100).toFixed(2) }})),
                        borderColor: m.color,
                        borderDash: [5, 4],
                        borderWidth: 1.8,
                        tension: 0.25,
                        pointRadius: 0
                    }});
                }}
            }});

            modelInspectionChart.data.datasets = datasets;
            modelInspectionChart.options.scales.x.max = maxEpoch || 100;
            modelInspectionChart.options.scales.y.title = {{
                display: true,
                text: activeChartMetric === 'loss' ? 'Validation Loss Comparison' : 'Metric Percentage (%)',
                color: '#6b7280'
            }};
            modelInspectionChart.update();
        }}

        // Initialize Pareto Scatter Chart
        function initParetoScatterChart() {{
            const canvas = document.getElementById('paretoScatterChart');
            if (!canvas) return;

            if (typeof Chart === 'undefined') {{
                renderOfflineSvgPareto();
                return;
            }}

            const ctx = canvas.getContext('2d');
            const scatterData = BENCHMARK_DATA.models.map(m => ({{
                x: m.params_m,
                y: m.global_iou,
                name: m.short_name,
                id: m.id,
                paradigm: m.paradigm,
                color: m.color
            }}));

            paretoScatterChart = new Chart(ctx, {{
                type: 'scatter',
                data: {{
                    datasets: [
                        {{
                            label: 'Models (Params vs IoU)',
                            data: scatterData,
                            backgroundColor: scatterData.map(d => d.color),
                            borderColor: '#ffffff',
                            borderWidth: 1.5,
                            pointRadius: 7,
                            pointHoverRadius: 10
                        }},
                        {{
                            label: 'Pareto Optimal Frontier',
                            type: 'line',
                            data: [
                                {{ x: 6.25, y: 76.56 }},
                                {{ x: 24.46, y: 81.66 }}
                            ],
                            borderColor: 'rgba(6, 182, 212, 0.6)',
                            borderDash: [6, 4],
                            borderWidth: 2,
                            fill: false,
                            pointRadius: 0
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    onClick: (event, elements) => {{
                        if (elements && elements.length > 0) {{
                            const idx = elements[0].index;
                            const datasetIdx = elements[0].datasetIndex;
                            if (datasetIdx === 0) {{
                                const clicked = BENCHMARK_DATA.models[idx];
                                if (clicked) {{
                                    selectModel(clicked.id);
                                    const target = document.getElementById('model-inspector');
                                    if (target) target.scrollIntoView({{ behavior: 'smooth' }});
                                }}
                            }}
                        }}
                    }},
                    onHover: (event, elements) => {{
                        event.native.target.style.cursor = (elements && elements.length > 0) ? 'pointer' : 'default';
                    }},
                    plugins: {{
                        tooltip: {{
                            callbacks: {{
                                label: (ctx) => {{
                                    const raw = ctx.raw;
                                    if (raw.name) {{
                                        return `${{raw.name}}: ${{raw.y}}% IoU (${{raw.x}}M Params) [Click to inspect]`;
                                    }}
                                    return `Frontier: ${{raw.y}}% IoU`;
                                }}
                            }}
                        }},
                        legend: {{
                            labels: {{ color: '#9ca3af', font: {{ family: 'JetBrains Mono', size: 10 }} }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                            ticks: {{ color: '#9ca3af', font: {{ family: 'JetBrains Mono' }} }},
                            title: {{ display: true, text: 'Parameters (Millions)', color: '#6b7280' }}
                        }},
                        y: {{
                            grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                            ticks: {{ color: '#9ca3af', font: {{ family: 'JetBrains Mono' }} }},
                            title: {{ display: true, text: 'Global Pixel IoU (%)', color: '#6b7280' }},
                            min: 60,
                            max: 85
                        }}
                    }}
                }}
            }});
        }}

        // Initialize Metrics Bar Chart
        function initMetricsBarChart() {{
            const canvas = document.getElementById('metricsBarChart');
            if (!canvas) return;

            if (typeof Chart === 'undefined') {{
                renderOfflineSvgMetrics();
                return;
            }}

            const ctx = canvas.getContext('2d');
            const models = BENCHMARK_DATA.models;

            metricsBarChart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: models.map(m => m.short_name),
                    datasets: [
                        {{
                            label: 'Global IoU (%)',
                            data: models.map(m => m.global_iou),
                            backgroundColor: '#10b981'
                        }},
                        {{
                            label: 'F1-Score (%)',
                            data: models.map(m => m.f1_score),
                            backgroundColor: '#06b6d4'
                        }},
                        {{
                            label: 'Precision (%)',
                            data: models.map(m => m.precision),
                            backgroundColor: '#3b82f6'
                        }},
                        {{
                            label: 'Recall (%)',
                            data: models.map(m => m.recall),
                            backgroundColor: '#8b5cf6'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    onClick: (event, elements) => {{
                        if (elements && elements.length > 0) {{
                            const idx = elements[0].index;
                            const clicked = BENCHMARK_DATA.models[idx];
                            if (clicked) {{
                                selectModel(clicked.id);
                                const target = document.getElementById('model-inspector');
                                if (target) target.scrollIntoView({{ behavior: 'smooth' }});
                            }}
                        }}
                    }},
                    onHover: (event, elements) => {{
                        event.native.target.style.cursor = (elements && elements.length > 0) ? 'pointer' : 'default';
                    }},
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            callbacks: {{
                                afterTitle: () => '[Click bar to inspect model curves]'
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            grid: {{ display: false }},
                            ticks: {{ color: '#9ca3af', font: {{ family: 'JetBrains Mono', size: 9 }} }}
                        }},
                        y: {{
                            grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                            ticks: {{ color: '#9ca3af', font: {{ family: 'JetBrains Mono', size: 10 }} }},
                            min: 60,
                            max: 100
                        }}
                    }}
                }}
            }});
        }}

        // Render Benchmark Table
        function renderBenchmarkTable() {{
            const tbody = document.getElementById('benchmark-table-body');
            if (!tbody) return;
            tbody.innerHTML = '';

            let filtered = BENCHMARK_DATA.models;
            if (activeTableFilter === '12ch') {{
                filtered = filtered.filter(m => m.bands === 12);
            }} else if (activeTableFilter === '6ch') {{
                filtered = filtered.filter(m => m.bands === 6);
            }} else if (activeTableFilter === 'transfer') {{
                filtered = filtered.filter(m => m.paradigm === 'Transfer Learning');
            }} else if (activeTableFilter === 'scratch') {{
                filtered = filtered.filter(m => m.paradigm !== 'Transfer Learning');
            }}

            filtered.forEach(m => {{
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-gray-800/40 transition cursor-pointer';
                tr.onclick = (e) => {{
                    if (!e.target.closest('button')) {{
                        selectModel(m.id);
                        document.getElementById('model-inspector').scrollIntoView({{ behavior: 'smooth' }});
                    }}
                }};

                tr.innerHTML = `
                    <td class="py-3 px-4 font-bold text-white flex items-center space-x-2">
                        <span class="w-2 h-2 rounded-full" style="background-color: ${{m.color}}"></span>
                        <span>${{m.id}}</span>
                        ${{m.is_champion ? '<span class="px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[9px]">SOTA</span>' : ''}}
                    </td>
                    <td class="py-3 px-3 text-gray-300">${{m.architecture}}</td>
                    <td class="py-3 px-3">
                        <span class="px-2 py-0.5 rounded text-[10px] ${{m.bands === 12 ? 'bg-cyan-950 text-cyan-400 border border-cyan-800' : 'bg-teal-950 text-teal-400 border border-teal-800'}}">
                            ${{m.band_type}}
                        </span>
                    </td>
                    <td class="py-3 px-3 text-right text-gray-300">${{m.params_m}}M</td>
                    <td class="py-3 px-3 text-right font-black text-emerald-400">${{m.global_iou.toFixed(2)}}%</td>
                    <td class="py-3 px-3 text-right text-gray-200">${{m.precision.toFixed(2)}}%</td>
                    <td class="py-3 px-3 text-right text-gray-200">${{m.recall.toFixed(2)}}%</td>
                    <td class="py-3 px-3 text-right font-bold text-cyan-400">${{m.f1_score.toFixed(2)}}%</td>
                    <td class="py-3 px-3 text-right text-gray-400">${{m.duration_s.toFixed(1)}} s</td>
                    <td class="py-3 px-4 text-center">
                        <button onclick="selectModel('${{m.id}}'); document.getElementById('model-inspector').scrollIntoView({{ behavior: 'smooth' }});" class="px-2.5 py-1 rounded bg-cyan-950/60 hover:bg-cyan-900 text-cyan-300 border border-cyan-800/80 text-[10px] transition">
                            View Curve
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function filterBenchmarkTable(filter) {{
            activeTableFilter = filter;
            ['all', '12ch', '6ch', 'transfer', 'scratch'].forEach(f => {{
                const btn = document.getElementById(`filter-btn-${{f}}`);
                if (btn) {{
                    if (f === filter) {{
                        btn.className = 'px-3 py-1.5 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 font-semibold transition';
                    }} else {{
                        btn.className = 'px-3 py-1.5 rounded-lg text-gray-400 hover:text-white transition';
                    }}
                }}
            }});
            renderBenchmarkTable();
        }}

        // Render Spectral Bands Grid
        function renderSpectralBands() {{
            const container = document.getElementById('spectral-bands-grid');
            if (!container) return;
            container.innerHTML = '';

            BENCHMARK_DATA.bands.forEach(b => {{
                const card = document.createElement('div');
                card.className = `p-3 rounded-xl border text-xs font-mono transition cursor-pointer select-none ${{b.golden ? 'bg-gray-900/90 border-emerald-500/50 shadow-sm shadow-emerald-500/10 hover:border-emerald-400' : 'bg-gray-900/40 border-gray-800 opacity-60 hover:opacity-90'}}`;
                card.onclick = () => highlightBandInSimulator(b.name);

                card.innerHTML = `
                    <div class="flex items-center justify-between">
                        <span class="font-black text-sm" style="color: ${{b.color}}">${{b.name}}</span>
                        <span class="text-[9px] px-1.5 py-0.5 rounded ${{b.golden ? 'bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold' : 'bg-gray-800 text-gray-400'}}">
                            ${{b.golden ? 'GOLDEN' : 'DISCARDED'}}
                        </span>
                    </div>
                    <div class="text-xs font-bold text-white mt-1">${{b.label}}</div>
                    <div class="text-[10px] text-gray-400 mt-1 flex justify-between">
                        <span>&lambda;: ${{b.wavelength_um}} µm</span>
                        <span>Res: ${{b.resolution_m}}m</span>
                    </div>
                    <div class="text-[9px] text-gray-400 mt-2 font-sans line-clamp-2 leading-tight">
                        ${{b.role}}
                    </div>
                `;
                container.appendChild(card);
            }});
        }}

        // Highlight Band in NDWI Simulator
        function highlightBandInSimulator(bandName) {{
            const targets = {{
                'B3': 'container-slider-b3',
                'B8': 'container-slider-b8',
                'B11': 'container-slider-b11'
            }};
            const card = document.getElementById('ndwi-simulator-card');
            if (card) card.scrollIntoView({{ behavior: 'smooth' }});

            if (targets[bandName]) {{
                const el = document.getElementById(targets[bandName]);
                if (el) {{
                    el.classList.add('ring-2', 'ring-cyan-400', 'bg-cyan-950/30');
                    setTimeout(() => {{
                        el.classList.remove('ring-2', 'ring-cyan-400', 'bg-cyan-950/30');
                    }}, 1500);
                }}
            }}
        }}

        // NDWI Live Calculator
        function calculateLiveNdwi() {{
            const b3 = parseFloat(document.getElementById('slider-b3').value);
            const b8 = parseFloat(document.getElementById('slider-b8').value);
            const b11 = parseFloat(document.getElementById('slider-b11').value);

            document.getElementById('val-b3').innerText = b3.toFixed(2);
            document.getElementById('val-b8').innerText = b8.toFixed(2);
            document.getElementById('val-b11').innerText = b11.toFixed(2);

            // NDWI = (B3 - B8) / (B3 + B8)
            let ndwi = 0;
            if (b3 + b8 > 0.0001) {{
                ndwi = (b3 - b8) / (b3 + b8);
            }}
            const ndwiValEl = document.getElementById('ndwi-result-val');
            const ndwiBadgeEl = document.getElementById('ndwi-status-badge');
            ndwiValEl.innerText = (ndwi >= 0 ? '+' : '') + ndwi.toFixed(3);

            if (ndwi > 0.0) {{
                ndwiValEl.className = 'text-3xl font-black text-cyan-400';
                ndwiBadgeEl.className = 'px-2 py-0.5 rounded text-[10px] bg-cyan-950 text-cyan-300 border border-cyan-800 font-bold inline-block';
                ndwiBadgeEl.innerText = 'Water Body Confirmed (> 0.0)';
            }} else {{
                ndwiValEl.className = 'text-3xl font-black text-gray-400';
                ndwiBadgeEl.className = 'px-2 py-0.5 rounded text-[10px] bg-gray-800 text-gray-400 border border-gray-700 font-bold inline-block';
                ndwiBadgeEl.innerText = 'Land / Canopy (<= 0.0)';
            }}

            // MNDWI = (B3 - B11) / (B3 + B11)
            let mndwi = 0;
            if (b3 + b11 > 0.0001) {{
                mndwi = (b3 - b11) / (b3 + b11);
            }}
            const mndwiValEl = document.getElementById('mndwi-result-val');
            const mndwiBadgeEl = document.getElementById('mndwi-status-badge');
            mndwiValEl.innerText = (mndwi >= 0 ? '+' : '') + mndwi.toFixed(3);

            if (mndwi > 0.0) {{
                mndwiValEl.className = 'text-3xl font-black text-emerald-400';
                mndwiBadgeEl.className = 'px-2 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-800 font-bold inline-block';
                mndwiBadgeEl.innerText = 'Clear Water Body';
            }} else {{
                mndwiValEl.className = 'text-3xl font-black text-gray-400';
                ndwiBadgeEl.className = 'px-2 py-0.5 rounded text-[10px] bg-gray-800 text-gray-400 border border-gray-700 font-bold inline-block';
                mndwiBadgeEl.innerText = 'Terrestrial / Soil';
            }}
        }}

        function setNdwiPreset(b3, b8, b11) {{
            document.getElementById('slider-b3').value = b3;
            document.getElementById('slider-b8').value = b8;
            document.getElementById('slider-b11').value = b11;
            calculateLiveNdwi();
        }}

        // ==========================================
        // 100% OFFLINE SVG FALLBACK RENDER ENGINE
        // Guarantees zero blank boxes if Chart.js CDN is unavailable
        // ==========================================
        function renderOfflineSvgCurve() {{
            const canvas = document.getElementById('modelInspectionChart');
            const fallback = document.getElementById('offline-chart-fallback');
            if (canvas) canvas.classList.add('hidden');
            if (!fallback) return;
            fallback.classList.remove('hidden');

            const model = BENCHMARK_DATA.models.find(m => m.id === activeModelId);
            if (!model || !model.epochs || model.epochs.length === 0) return;

            const epochs = model.epochs;
            const width = 800;
            const height = 360;
            const padding = {{ top: 30, right: 30, bottom: 40, left: 55 }};
            const innerW = width - padding.left - padding.right;
            const innerH = height - padding.top - padding.bottom;

            const maxEpoch = Math.max(...epochs.map(e => e.epoch));
            const yVals = activeChartMetric === 'loss' 
                ? epochs.flatMap(e => [e.train_loss, e.val_loss])
                : (activeChartMetric === 'iou' ? epochs.map(e => e.val_iou * 100) : epochs.flatMap(e => [e.precision * 100, e.recall * 100]));
            const minY = Math.min(...yVals) * 0.9;
            const maxY = Math.max(...yVals) * 1.05;

            const getX = (ep) => padding.left + ((ep - 1) / (maxEpoch - 1)) * innerW;
            const getY = (val) => padding.top + innerH - ((val - minY) / (maxY - minY)) * innerH;

            const trainPts = epochs.map(e => `${{getX(e.epoch)}},${{getY(activeChartMetric === 'loss' ? e.train_loss : e.val_iou * 100)}}`).join(' ');
            const valPts = activeChartMetric === 'loss' ? epochs.map(e => `${{getX(e.epoch)}},${{getY(e.val_loss)}}`).join(' ') : '';

            // Warmup line
            let warmupSvg = '';
            if (model.warmup_epochs > 0) {{
                const wx = getX(model.warmup_epochs);
                warmupSvg = `
                    <line x1="${{wx}}" y1="${{padding.top}}" x2="${{wx}}" y2="${{padding.top + innerH}}" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="4,4"/>
                    <text x="${{wx - 6}}" y="${{padding.top + 16}}" fill="#f59e0b" font-size="10" font-family="monospace" text-anchor="end">Warmup (Ep 1-${{model.warmup_epochs}})</text>
                    <text x="${{wx + 6}}" y="${{padding.top + 16}}" fill="#10b981" font-size="10" font-family="monospace">Fine-Tune →</text>
                `;
            }}

            fallback.innerHTML = `
                <svg viewBox="0 0 ${{width}} ${{height}}" class="w-full h-full font-mono text-xs">
                    <!-- Background Grid -->
                    <rect x="${{padding.left}}" y="${{padding.top}}" width="${{innerW}}" height="${{innerH}}" fill="#0b0f19" stroke="#1f2937"/>
                    <line x1="${{padding.left}}" y1="${{padding.top + innerH/2}}" x2="${{padding.left + innerW}}" y2="${{padding.top + innerH/2}}" stroke="rgba(255,255,255,0.05)"/>
                    <line x1="${{padding.left}}" y1="${{padding.top + innerH/4}}" x2="${{padding.left + innerW}}" y2="${{padding.top + innerH/4}}" stroke="rgba(255,255,255,0.05)"/>
                    <line x1="${{padding.left}}" y1="${{padding.top + 3*innerH/4}}" x2="${{padding.left + innerW}}" y2="${{padding.top + 3*innerH/4}}" stroke="rgba(255,255,255,0.05)"/>
                    
                    ${{warmupSvg}}

                    <!-- Curves -->
                    <polyline fill="none" stroke="#38bdf8" stroke-width="2.2" points="${{trainPts}}"/>
                    ${{valPts ? `<polyline fill="none" stroke="#fbbf24" stroke-width="2.2" points="${{valPts}}"/>` : ''}}

                    <!-- Offline Badge -->
                    <rect x="${{width - 240}}" y="10" width="220" height="20" rx="4" fill="#1e293b"/>
                    <text x="${{width - 130}}" y="24" fill="#38bdf8" font-size="10" text-anchor="middle">Offline Mode (Native SVG Active)</text>

                    <!-- Axis Labels -->
                    <text x="${{padding.left}}" y="${{height - 10}}" fill="#6b7280" font-size="10">Epoch 1</text>
                    <text x="${{width - padding.right}}" y="${{height - 10}}" fill="#6b7280" font-size="10" text-anchor="end">Epoch ${{maxEpoch}}</text>
                    <text x="${{padding.left - 10}}" y="${{padding.top + 10}}" fill="#6b7280" font-size="10" text-anchor="end">${{maxY.toFixed(2)}}</text>
                    <text x="${{padding.left - 10}}" y="${{padding.top + innerH}}" fill="#6b7280" font-size="10" text-anchor="end">${{minY.toFixed(2)}}</text>
                </svg>
            `;
        }}

        function renderOfflineSvgPareto() {{
            const canvas = document.getElementById('paretoScatterChart');
            const fallback = document.getElementById('offline-pareto-fallback');
            if (canvas) canvas.classList.add('hidden');
            if (!fallback) return;
            fallback.classList.remove('hidden');

            const width = 600;
            const height = 340;
            const padding = {{ top: 30, right: 30, bottom: 40, left: 50 }};
            const innerW = width - padding.left - padding.right;
            const innerH = height - padding.top - padding.bottom;

            const models = BENCHMARK_DATA.models;
            const minX = 0, maxX = 30;
            const minY = 60, maxY = 85;

            const getX = (p) => padding.left + (p / maxX) * innerW;
            const getY = (iou) => padding.top + innerH - ((iou - minY) / (maxY - minY)) * innerH;

            const dots = models.map(m => `
                <circle cx="${{getX(m.params_m)}}" cy="${{getY(m.global_iou)}}" r="6" fill="${{m.color}}" stroke="#fff" stroke-width="1.5" class="cursor-pointer" onclick="selectModel('${{m.id}}')"/>
                <text x="${{getX(m.params_m) + 8}}" y="${{getY(m.global_iou) + 4}}" fill="${{m.color}}" font-size="9" font-family="monospace">${{m.short_name}}</text>
            `).join('');

            fallback.innerHTML = `
                <svg viewBox="0 0 ${{width}} ${{height}}" class="w-full h-full font-mono">
                    <rect x="${{padding.left}}" y="${{padding.top}}" width="${{innerW}}" height="${{innerH}}" fill="#0b0f19" stroke="#1f2937"/>
                    <line x1="${{getX(6.25)}}" y1="${{getY(76.56)}}" x2="${{getX(24.46)}}" y2="${{getY(81.66)}}" stroke="rgba(6, 182, 212, 0.6)" stroke-width="2" stroke-dasharray="6,4"/>
                    ${{dots}}
                    <text x="${{padding.left}}" y="${{height - 10}}" fill="#6b7280" font-size="10">0M</text>
                    <text x="${{width - padding.right}}" y="${{height - 10}}" fill="#6b7280" font-size="10" text-anchor="end">30M Params</text>
                </svg>
            `;
        }}

        function renderOfflineSvgMetrics() {{
            const canvas = document.getElementById('metricsBarChart');
            const fallback = document.getElementById('offline-metrics-fallback');
            if (canvas) canvas.classList.add('hidden');
            if (!fallback) return;
            fallback.classList.remove('hidden');

            const width = 500;
            const height = 340;
            const padding = {{ top: 30, right: 20, bottom: 60, left: 45 }};
            const innerW = width - padding.left - padding.right;
            const innerH = height - padding.top - padding.bottom;

            const models = BENCHMARK_DATA.models;
            const slotW = innerW / models.length;
            const barW = slotW * 0.7;

            const bars = models.map((m, i) => {{
                const x = padding.left + i * slotW + (slotW - barW) / 2;
                const barH = ((m.global_iou - 50) / 50) * innerH;
                const y = padding.top + innerH - barH;
                return `
                    <rect x="${{x}}" y="${{y}}" width="${{barW}}" height="${{barH}}" fill="${{m.color}}" rx="2" class="cursor-pointer" onclick="selectModel('${{m.id}}')"/>
                    <text x="${{x + barW/2}}" y="${{height - 40}}" fill="#9ca3af" font-size="8" font-family="monospace" text-anchor="middle" transform="rotate(-30, ${{x + barW/2}}, ${{height - 40}})">${{m.short_name}}</text>
                    <text x="${{x + barW/2}}" y="${{y - 4}}" fill="#10b981" font-size="8" font-family="monospace" text-anchor="middle">${{m.global_iou.toFixed(1)}}%</text>
                `;
            }}).join('');

            fallback.innerHTML = `
                <svg viewBox="0 0 ${{width}} ${{height}}" class="w-full h-full font-mono">
                    <rect x="${{padding.left}}" y="${{padding.top}}" width="${{innerW}}" height="${{innerH}}" fill="#0b0f19" stroke="#1f2937"/>
                    ${{bars}}
                </svg>
            `;
        }}

        // Export JSON Data
        function downloadBenchmarkJSON() {{
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(BENCHMARK_DATA, null, 2));
            const downloadAnchor = document.createElement('a');
            downloadAnchor.setAttribute("href", dataStr);
            downloadAnchor.setAttribute("download", "hydroflow_benchmark_data.json");
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            downloadAnchor.remove();
        }}

        // Copy Citation
        function copyBibtexCitation() {{
            const bibtex = `@misc{{elbasyouni2026hydroflow,
  author = {{Mohamed Mostafa Elbasyouni}},
  title = {{HydroFlow: Multispectral 12-Channel Satellite Water Segmentation, Optimal Transport Flow Matching, and Transfer Learning}},
  year = {{2026}},
  publisher = {{GitHub}},
  howpublished = {{https://github.com/markegyptian55-cloud/HydroFlow-12Channel-Water-Segmentation}}
}}`;
            navigator.clipboard.writeText(bibtex).then(() => {{
                alert("BibTeX citation copied to clipboard!");
            }});
        }}
    </script>
</body>
</html>
"""

    # 1. Write reports/interactive_dashboard.html
    report_file = 'reports/interactive_dashboard.html'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated {report_file} ({len(html_content)} bytes).")

    # 2. Write dashboard.html at root as identical standalone launcher
    root_file = 'dashboard.html'
    with open(root_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated {root_file} ({len(html_content)} bytes).")

if __name__ == '__main__':
    build_dashboard()
