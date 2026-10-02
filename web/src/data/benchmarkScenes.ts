export interface SpectralProfile {
  band: string;
  name: string;
  wavelength: number;
  water: number;
  vegetation: number;
  soil: number;
}

export interface BenchmarkScene {
  id: string;
  name: string;
  region: string;
  country: string;
  coordinates: { lat: number; lng: number };
  coordinatesDisplay: string;
  captureDate: string;
  waterAreaKm2: number;
  shorelineKm: number;
  meanConfidence: number;
  validationIoU: number;
  description: string;
  spectralProfiles: SpectralProfile[];
  svgPathWater: string;
  svgPathCoastline: string;
}

export const BENCHMARK_SCENES: BenchmarkScene[] = [
  {
    id: "lake-nasser",
    name: "Lake Nasser & Aswan High Dam",
    region: "Nile River Valley",
    country: "Egypt",
    coordinates: { lat: 23.97, lng: 32.88 },
    coordinatesDisplay: "23° 58' N, 32° 52' E",
    captureDate: "2024-03-14",
    waterAreaKm2: 5248.5,
    shorelineKm: 7840.2,
    meanConfidence: 96.8,
    validationIoU: 74.2,
    description: "One of the largest artificial reservoirs in the world. High contrast between arid Saharan sandstone and deep reservoir water highlights SWIR and NIR absorption.",
    spectralProfiles: [
      { band: "B1", name: "Coastal", wavelength: 0.443, water: 0.082, vegetation: 0.045, soil: 0.142 },
      { band: "B2", name: "Blue", wavelength: 0.490, water: 0.075, vegetation: 0.052, soil: 0.178 },
      { band: "B3", name: "Green", wavelength: 0.560, water: 0.068, vegetation: 0.098, soil: 0.224 },
      { band: "B4", name: "Red", wavelength: 0.665, water: 0.042, vegetation: 0.055, soil: 0.285 },
      { band: "B5", name: "RE1", wavelength: 0.705, water: 0.031, vegetation: 0.165, soil: 0.312 },
      { band: "B6", name: "RE2", wavelength: 0.740, water: 0.022, vegetation: 0.380, soil: 0.334 },
      { band: "B7", name: "RE3", wavelength: 0.783, water: 0.016, vegetation: 0.450, soil: 0.348 },
      { band: "B8", name: "NIR", wavelength: 0.842, water: 0.012, vegetation: 0.485, soil: 0.355 },
      { band: "B8A", name: "NNIR", wavelength: 0.865, water: 0.010, vegetation: 0.490, soil: 0.360 },
      { band: "B9", name: "Vapour", wavelength: 0.945, water: 0.005, vegetation: 0.440, soil: 0.320 },
      { band: "B11", name: "SWIR1", wavelength: 1.610, water: 0.003, vegetation: 0.220, soil: 0.410 },
      { band: "B12", name: "SWIR2", wavelength: 2.190, water: 0.002, vegetation: 0.095, soil: 0.385 }
    ],
    svgPathWater: "M 30,0 Q 80,120 180,160 T 320,240 Q 380,300 350,420 T 400,600 L 0,600 L 0,0 Z",
    svgPathCoastline: "M 30,0 Q 80,120 180,160 T 320,240 Q 380,300 350,420 T 400,600"
  },
  {
    id: "suez-canal",
    name: "Suez Canal & Great Bitter Lake",
    region: "Isthmus of Suez",
    country: "Egypt",
    coordinates: { lat: 30.45, lng: 32.35 },
    coordinatesDisplay: "30° 27' N, 32° 21' E",
    captureDate: "2024-04-02",
    waterAreaKm2: 250.0,
    shorelineKm: 193.3,
    meanConfidence: 95.4,
    validationIoU: 72.8,
    description: "Crucial maritime trade corridor. Features narrow navigational channels with sharp urban/desert boundaries and dynamic ship traffic wake disturbances.",
    spectralProfiles: [
      { band: "B1", name: "Coastal", wavelength: 0.443, water: 0.090, vegetation: 0.050, soil: 0.150 },
      { band: "B2", name: "Blue", wavelength: 0.490, water: 0.082, vegetation: 0.060, soil: 0.190 },
      { band: "B3", name: "Green", wavelength: 0.560, water: 0.071, vegetation: 0.110, soil: 0.240 },
      { band: "B4", name: "Red", wavelength: 0.665, water: 0.045, vegetation: 0.060, soil: 0.300 },
      { band: "B5", name: "RE1", wavelength: 0.705, water: 0.033, vegetation: 0.180, soil: 0.320 },
      { band: "B6", name: "RE2", wavelength: 0.740, water: 0.024, vegetation: 0.390, soil: 0.340 },
      { band: "B7", name: "RE3", wavelength: 0.783, water: 0.018, vegetation: 0.460, soil: 0.350 },
      { band: "B8", name: "NIR", wavelength: 0.842, water: 0.014, vegetation: 0.490, soil: 0.360 },
      { band: "B8A", name: "NNIR", wavelength: 0.865, water: 0.012, vegetation: 0.495, soil: 0.365 },
      { band: "B9", name: "Vapour", wavelength: 0.945, water: 0.007, vegetation: 0.450, soil: 0.330 },
      { band: "B11", name: "SWIR1", wavelength: 1.610, water: 0.004, vegetation: 0.230, soil: 0.420 },
      { band: "B12", name: "SWIR2", wavelength: 2.190, water: 0.002, vegetation: 0.100, soil: 0.390 }
    ],
    svgPathWater: "M 280,0 L 320,0 L 330,220 Q 420,280 400,380 Q 320,440 310,600 L 270,600 L 280,440 Q 240,360 270,260 Z",
    svgPathCoastline: "M 280,0 L 270,260 Q 240,360 280,440 L 270,600 M 320,0 L 330,220 Q 420,280 400,380 Q 320,440 310,600"
  },
  {
    id: "venice-lagoon",
    name: "Venice Lagoon & Coastal Marshes",
    region: "Adriatic Coast",
    country: "Italy",
    coordinates: { lat: 45.43, lng: 12.33 },
    coordinatesDisplay: "45° 26' N, 12° 20' E",
    captureDate: "2024-05-18",
    waterAreaKm2: 550.2,
    shorelineKm: 1420.6,
    meanConfidence: 94.1,
    validationIoU: 71.5,
    description: "Complex wetland ecosystem with salt marshes, mudflats, and tidal channels. Stresses model boundary segmentation on shallow turbid water.",
    spectralProfiles: [
      { band: "B1", name: "Coastal", wavelength: 0.443, water: 0.095, vegetation: 0.040, soil: 0.120 },
      { band: "B2", name: "Blue", wavelength: 0.490, water: 0.088, vegetation: 0.050, soil: 0.150 },
      { band: "B3", name: "Green", wavelength: 0.560, water: 0.079, vegetation: 0.120, soil: 0.190 },
      { band: "B4", name: "Red", wavelength: 0.665, water: 0.055, vegetation: 0.050, soil: 0.220 },
      { band: "B5", name: "RE1", wavelength: 0.705, water: 0.040, vegetation: 0.210, soil: 0.240 },
      { band: "B6", name: "RE2", wavelength: 0.740, water: 0.030, vegetation: 0.420, soil: 0.260 },
      { band: "B7", name: "RE3", wavelength: 0.783, water: 0.022, vegetation: 0.480, soil: 0.270 },
      { band: "B8", name: "NIR", wavelength: 0.842, water: 0.018, vegetation: 0.510, soil: 0.280 },
      { band: "B8A", name: "NNIR", wavelength: 0.865, water: 0.015, vegetation: 0.515, soil: 0.285 },
      { band: "B9", name: "Vapour", wavelength: 0.945, water: 0.009, vegetation: 0.460, soil: 0.250 },
      { band: "B11", name: "SWIR1", wavelength: 1.610, water: 0.005, vegetation: 0.210, soil: 0.310 },
      { band: "B12", name: "SWIR2", wavelength: 2.190, water: 0.003, vegetation: 0.090, soil: 0.280 }
    ],
    svgPathWater: "M 50,80 Q 180,40 260,120 T 450,140 Q 520,240 480,360 T 360,520 Q 220,580 120,490 T 40,320 Q 10,180 50,80 Z M 160,220 Q 220,190 260,250 T 210,340 Q 150,330 160,220 Z",
    svgPathCoastline: "M 50,80 Q 180,40 260,120 T 450,140 Q 520,240 480,360 T 360,520 Q 220,580 120,490 T 40,320 Q 10,180 50,80 M 160,220 Q 220,190 260,250 T 210,340 Q 150,330 160,220"
  },
  {
    id: "lake-mead",
    name: "Lake Mead & Hoover Dam",
    region: "Colorado River Basin",
    country: "United States",
    coordinates: { lat: 36.01, lng: -114.74 },
    coordinatesDisplay: "36° 01' N, 114° 44' W",
    captureDate: "2024-06-11",
    waterAreaKm2: 640.0,
    shorelineKm: 1320.0,
    meanConfidence: 97.2,
    validationIoU: 73.8,
    description: "Major Colorado River reservoir surrounded by steep canyon topography. Prominent 'bathtub ring' mineral exposure visible along retreating shorelines.",
    spectralProfiles: [
      { band: "B1", name: "Coastal", wavelength: 0.443, water: 0.080, vegetation: 0.040, soil: 0.160 },
      { band: "B2", name: "Blue", wavelength: 0.490, water: 0.073, vegetation: 0.048, soil: 0.200 },
      { band: "B3", name: "Green", wavelength: 0.560, water: 0.065, vegetation: 0.090, soil: 0.250 },
      { band: "B4", name: "Red", wavelength: 0.665, water: 0.040, vegetation: 0.050, soil: 0.320 },
      { band: "B5", name: "RE1", wavelength: 0.705, water: 0.029, vegetation: 0.150, soil: 0.350 },
      { band: "B6", name: "RE2", wavelength: 0.740, water: 0.020, vegetation: 0.340, soil: 0.370 },
      { band: "B7", name: "RE3", wavelength: 0.783, water: 0.015, vegetation: 0.410, soil: 0.380 },
      { band: "B8", name: "NIR", wavelength: 0.842, water: 0.011, vegetation: 0.440, soil: 0.390 },
      { band: "B8A", name: "NNIR", wavelength: 0.865, water: 0.009, vegetation: 0.445, soil: 0.395 },
      { band: "B9", name: "Vapour", wavelength: 0.945, water: 0.005, vegetation: 0.400, soil: 0.350 },
      { band: "B11", name: "SWIR1", wavelength: 1.610, water: 0.003, vegetation: 0.200, soil: 0.450 },
      { band: "B12", name: "SWIR2", wavelength: 2.190, water: 0.001, vegetation: 0.080, soil: 0.420 }
    ],
    svgPathWater: "M 0,220 Q 140,240 220,180 T 360,110 Q 480,80 540,160 T 520,320 Q 420,380 340,310 T 180,360 Q 90,420 0,380 Z",
    svgPathCoastline: "M 0,220 Q 140,240 220,180 T 360,110 Q 480,80 540,160 T 520,320 Q 420,380 340,310 T 180,360 Q 90,420 0,380"
  }
];
