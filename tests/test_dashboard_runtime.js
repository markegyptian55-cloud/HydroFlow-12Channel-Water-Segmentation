const fs = require('fs');

const html = fs.readFileSync('dashboard.html', 'utf-8');

// 1. Check syntax of all script tags
const scripts = [...html.matchAll(/<script[\s\S]*?>([\s\S]*?)<\/script>/gi)];
console.log('Script tags count:', scripts.length);

let jsCode = '';
for (const s of scripts) {
    const code = s[1].trim();
    if (code.includes('BENCHMARK_DATA') || code.includes('function selectModel')) {
        jsCode += code + '\n';
    }
}

// 2. Mock DOM environment for full functional testing
class MockClassList {
    constructor() { this.classes = new Set(); }
    add(...cls) { cls.forEach(c => c.split(' ').forEach(x => x && this.classes.add(x))); }
    remove(...cls) { cls.forEach(c => c.split(' ').forEach(x => x && this.classes.delete(x))); }
    toggle(c) { if (this.classes.has(c)) this.classes.delete(c); else this.classes.add(c); }
    contains(c) { return this.classes.has(c); }
}

class MockElement {
    constructor(id = '', tag = 'div') {
        this.id = id;
        this.tagName = tag;
        this.innerHTML = '';
        this.innerText = '';
        this.value = '0.22';
        this.checked = false;
        this.classList = new MockClassList();
        this.style = {};
        this.children = [];
        this.parentElement = null;
    }
    appendChild(child) {
        this.children.push(child);
        child.parentElement = this;
        return child;
    }
    scrollIntoView() {}
    getContext() {
        return {
            save: () => {},
            restore: () => {},
            fillRect: () => {},
            strokeRect: () => {},
            beginPath: () => {},
            moveTo: () => {},
            lineTo: () => {},
            stroke: () => {},
            fillText: () => {},
            setLineDash: () => {},
            fillStyle: '',
            strokeStyle: '',
            lineWidth: 1,
            font: '',
            textAlign: ''
        };
    }
}

const elements = {};
function getOrCreateElement(id) {
    if (!elements[id]) elements[id] = new MockElement(id);
    return elements[id];
}

const documentMock = {
    getElementById: (id) => getOrCreateElement(id),
    createElement: (tag) => new MockElement('', tag),
    querySelector: (sel) => new MockElement(),
    querySelectorAll: (sel) => [],
    addEventListener: (evt, cb) => {
        if (evt === 'DOMContentLoaded') cb();
    }
};

// Mock Chart
class MockChart {
    constructor(ctx, config) {
        this.ctx = ctx;
        this.config = config;
        this.data = config.data || { datasets: [] };
        this.options = config.options || { scales: { x: {}, y: {} } };
        this.plugins = config.plugins || [];
        this.scales = {
            x: {
                left: 50, right: 750,
                getPixelForValue: (v) => 50 + v * 7
            },
            y: {
                top: 30, bottom: 330,
                getPixelForValue: (v) => 330 - v * 200
            }
        };
    }
    update() {}
}

const globalScope = {
    document: documentMock,
    window: {},
    Chart: MockChart,
    navigator: { clipboard: { writeText: () => Promise.resolve() } },
    alert: (msg) => {},
    console: console,
    setTimeout: (fn, ms) => fn(),
    Number: Number,
    Math: Math,
    JSON: JSON,
    parseFloat: parseFloat
};

// Execute JavaScript in test sandbox
const runContext = new Function(...Object.keys(globalScope), jsCode + `
    return {
        BENCHMARK_DATA,
        renderModelCards,
        selectModel,
        switchChartMetric,
        toggleOverlayMode,
        updateOverlaySelection,
        renderBenchmarkTable,
        filterBenchmarkTable,
        renderSpectralBands,
        highlightBandInSimulator,
        calculateLiveNdwi,
        setNdwiPreset,
        renderOfflineSvgCurve,
        renderOfflineSvgPareto,
        renderOfflineSvgMetrics,
        inspectionAnnotationsPlugin,
        getModelInspectionChart: () => modelInspectionChart,
        getParetoScatterChart: () => paretoScatterChart,
        getMetricsBarChart: () => metricsBarChart,
        getActiveModelId: () => activeModelId,
        getActiveChartMetric: () => activeChartMetric,
        getIsOverlayMode: () => isOverlayMode,
        getOverlaySelectedModels: () => overlaySelectedModels
    };
`);

const exportsObj = runContext(...Object.values(globalScope));

console.log('✅ Controller initialized successfully.');
console.log('Total models in dataset:', exportsObj.BENCHMARK_DATA.models.length);

// 3. Test selectModel on each of the 7 models
exportsObj.BENCHMARK_DATA.models.forEach(m => {
    exportsObj.selectModel(m.id);
    if (exportsObj.getActiveModelId() !== m.id) {
        throw new Error('Failed to select model ' + m.id);
    }
    console.log('  Tested selectModel -> ' + m.id + ' (Global IoU: ' + m.global_iou + '%)');
});

// 4. Test metric switches
['loss', 'iou', 'precision_recall'].forEach(metric => {
    exportsObj.switchChartMetric(metric);
    if (exportsObj.getActiveChartMetric() !== metric) {
        throw new Error('Failed to switch metric to ' + metric);
    }
    console.log('  Tested switchChartMetric -> ' + metric);
});

// 5. Test Overlay Mode
exportsObj.toggleOverlayMode(true);
if (!exportsObj.getIsOverlayMode()) throw new Error('Failed to enable overlay mode');
console.log('  Tested toggleOverlayMode(true) -> models:', exportsObj.getOverlaySelectedModels());

// Test metric switches in Overlay Mode
['loss', 'iou', 'precision_recall'].forEach(metric => {
    exportsObj.switchChartMetric(metric);
    console.log('  Tested overlay mode metric -> ' + metric);
});

// Test clicking a card in overlay mode ensures it is included
exportsObj.selectModel('W1-Scratch-6ch');
if (!exportsObj.getOverlaySelectedModels().includes('W1-Scratch-6ch')) {
    throw new Error('Model card clicked in overlay mode was not added to overlay selection!');
}
console.log('  Tested selectModel in overlay mode -> correctly auto-included W1-Scratch-6ch');

exportsObj.toggleOverlayMode(false);
console.log('  Tested toggleOverlayMode(false)');

// 6. Test Annotation Plugin Canvas Drawing
const chart = exportsObj.getModelInspectionChart();
exportsObj.selectModel('W2-Pretrained-ResNet34-12ch'); // Has warmup_epochs = 3, best_epoch = 29
exportsObj.inspectionAnnotationsPlugin.afterDraw(chart);
console.log('  Tested inspectionAnnotationsPlugin.afterDraw() without exceptions');

// 7. Test Table Filters
['all', '12ch', '6ch', 'transfer', 'scratch'].forEach(filter => {
    exportsObj.filterBenchmarkTable(filter);
    console.log('  Tested filterBenchmarkTable -> ' + filter);
});

// 8. Test NDWI and MNDWI presets
exportsObj.setNdwiPreset(0.22, 0.02, 0.01);
const ndwiValLake = getOrCreateElement('ndwi-result-val').innerText;
const ndwiBadgeLake = getOrCreateElement('ndwi-status-badge').innerText;
console.log('  Tested Deep Lake preset -> NDWI: ' + ndwiValLake + ' (' + ndwiBadgeLake + ')');

exportsObj.setNdwiPreset(0.08, 0.55, 0.20);
const ndwiValForest = getOrCreateElement('ndwi-result-val').innerText;
const ndwiBadgeForest = getOrCreateElement('ndwi-status-badge').innerText;
console.log('  Tested Forest preset -> NDWI: ' + ndwiValForest + ' (' + ndwiBadgeForest + ')');

// 9. Test Interactive Pareto & Metrics Bar Chart Click Handling
const pareto = exportsObj.getParetoScatterChart();
if (typeof pareto.options.onClick === 'function') {
    pareto.options.onClick({ native: { target: {} } }, [{ index: 0, datasetIndex: 0 }]);
    console.log('  Tested paretoScatterChart onClick -> active model is now:', exportsObj.getActiveModelId());
} else {
    throw new Error('paretoScatterChart missing onClick handler');
}

const metricsBar = exportsObj.getMetricsBarChart();
if (typeof metricsBar.options.onClick === 'function') {
    metricsBar.options.onClick({ native: { target: {} } }, [{ index: 2 }]);
    console.log('  Tested metricsBarChart onClick -> active model is now:', exportsObj.getActiveModelId());
} else {
    throw new Error('metricsBarChart missing onClick handler');
}

// 10. Test Offline SVG Fallbacks
exportsObj.renderOfflineSvgCurve();
const offlineCurveHtml = getOrCreateElement('offline-chart-fallback').innerHTML;
if (!offlineCurveHtml.includes('<svg') || !offlineCurveHtml.includes('polyline')) {
    throw new Error('Offline SVG Curve fallback failed to generate valid SVG');
}
console.log('  Tested renderOfflineSvgCurve() -> generated ' + offlineCurveHtml.length + ' chars of SVG');

exportsObj.renderOfflineSvgPareto();
const offlineParetoHtml = getOrCreateElement('offline-pareto-fallback').innerHTML;
if (!offlineParetoHtml.includes('<svg') || !offlineParetoHtml.includes('circle')) {
    throw new Error('Offline SVG Pareto fallback failed to generate valid SVG');
}
console.log('  Tested renderOfflineSvgPareto() -> generated ' + offlineParetoHtml.length + ' chars of SVG');

exportsObj.renderOfflineSvgMetrics();
const offlineMetricsHtml = getOrCreateElement('offline-metrics-fallback').innerHTML;
if (!offlineMetricsHtml.includes('<svg') || !offlineMetricsHtml.includes('rect')) {
    throw new Error('Offline SVG Metrics fallback failed to generate valid SVG');
}
console.log('  Tested renderOfflineSvgMetrics() -> generated ' + offlineMetricsHtml.length + ' chars of SVG');

console.log('\n🌟 ALL 10 TEST SUITES PASSED FLAWLESSLY WITH ZERO ERRORS!');
