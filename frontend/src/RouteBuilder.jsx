import React, { useState, useCallback, useRef } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, useMapEvents, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const LINE_COLORS = ['#ef4444', '#3b82f6', '#22c55e', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4'];

const makeIcon = (label, color) =>
  L.divIcon({
    className: '',
    html: `<div style="
      width:28px;height:28px;border-radius:50%;
      background:${color};border:2.5px solid white;
      box-shadow:0 1px 6px rgba(0,0,0,0.25);
      display:flex;align-items:center;justify-content:center;
      font-family:monospace;font-size:11px;font-weight:700;color:white;
    ">${label}</div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  });

const makeArrowIcon = (color, rotation) =>
  L.divIcon({
    className: '',
    html: `<svg width="14" height="14" viewBox="0 0 14 14" style="transform: rotate(${rotation}deg);">
      <polygon points="7,0 14,12 0,12" fill="${color}"/>
    </svg>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  });

const makeStopIcon = (index) =>
  L.divIcon({
    className: '',
    html: `<div style="
      width:18px;height:18px;border-radius:50%;
      background:#8b5cf6;border:2px solid white;
      box-shadow:0 1px 4px rgba(0,0,0,0.2);
      display:flex;align-items:center;justify-content:center;
      font-family:monospace;font-size:8px;font-weight:700;color:white;
    ">${index + 1}</div>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  });

const calcBearing = (lat1, lng1, lat2, lng2) => {
  const dLng = (lng2 - lng1) * (Math.PI / 180);
  const lat1Rad = lat1 * (Math.PI / 180);
  const lat2Rad = lat2 * (Math.PI / 180);
  const y = Math.sin(dLng) * Math.cos(lat2Rad);
  const x = Math.cos(lat1Rad) * Math.sin(lat2Rad) - Math.sin(lat1Rad) * Math.cos(lat2Rad) * Math.cos(dLng);
  let bearing = Math.atan2(y, x) * (180 / Math.PI);
  bearing = (bearing + 360) % 360;
  return bearing;
};

const DirectionalPolyline = ({ positions, color, weight = 5, opacity = 0.85, arrowSpacing = 8, stops = null }) => {
  if (!positions || positions.length < 2) return null;

  const arrowMarkers = [];
  for (let i = arrowSpacing; i < positions.length - 1; i += arrowSpacing) {
    const [lat1, lng1] = positions[i - 1];
    const [lat2, lng2] = positions[i];
    const midLat = (lat1 + lat2) / 2;
    const midLng = (lng1 + lng2) / 2;
    const bearing = calcBearing(lat1, lng1, lat2, lng2);
    arrowMarkers.push(
      <Marker
        key={`arrow-${i}`}
        position={[midLat, midLng]}
        icon={makeArrowIcon(color, bearing)}
      />
    );
  }

  const stopMarkers = stops
    ? stops.map((stop, idx) => (
        <Marker
          key={`stop-${stop.id || idx}`}
          position={[stop.lat, stop.lng]}
          icon={makeStopIcon(idx)}
        >
          <Tooltip sticky>
            <span className="font-mono text-[10px]">{stop.name}</span>
            {stop.street && (
              <span className="font-mono text-[9px] text-slate-400 block">{stop.street}</span>
            )}
          </Tooltip>
        </Marker>
      ))
    : null;

  return (
    <>
      <Polyline positions={positions} pathOptions={{ color, weight, opacity }} />
      {arrowMarkers}
      {stopMarkers}
    </>
  );
};

const ICON_A = makeIcon('A', '#3b82f6');
const ICON_B = makeIcon('B', '#ef4444');

const ClickHandler = ({ onMapClick }) => {
  useMapEvents({ click: (e) => onMapClick(e.latlng) });
  return null;
};

const coordsToString = (pt) =>
  pt ? `${pt.lat.toFixed(5)}, ${pt.lng.toFixed(5)}` : '';

const parseCoords = (str) => {
  const parts = str.split(',').map((s) => parseFloat(s.trim()));
  if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1])) {
    return { lat: parts[0], lng: parts[1] };
  }
  return null;
};

const RouteBuilder = () => {
  const [selectingFor, setSelectingFor] = useState(null); // 'A' | 'B' | null
  const [pointA, setPointA] = useState(null);
  const [pointB, setPointB] = useState(null);
  const [inputA, setInputA] = useState('');
  const [inputB, setInputB] = useState('');
  const [inputAError, setInputAError] = useState(false);
  const [inputBError, setInputBError] = useState(false);
  const [generatedRoute, setGeneratedRoute] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const routeCounterRef = useRef(1);

  const handleMapClick = useCallback(
    (latlng) => {
      if (!selectingFor) return;
      if (selectingFor === 'A') {
        setPointA(latlng);
        setInputA(coordsToString(latlng));
        setInputAError(false);
      } else {
        setPointB(latlng);
        setInputB(coordsToString(latlng));
        setInputBError(false);
      }
      setSelectingFor(null);
    },
    [selectingFor]
  );

  const handleInputChange = (which, value) => {
    if (which === 'A') {
      setInputA(value);
      setInputAError(false);
      const parsed = parseCoords(value);
      if (parsed) setPointA(parsed);
      else if (value.trim() === '') setPointA(null);
    } else {
      setInputB(value);
      setInputBError(false);
      const parsed = parseCoords(value);
      if (parsed) setPointB(parsed);
      else if (value.trim() === '') setPointB(null);
    }
  };

  const handleInputBlur = (which) => {
    const val = which === 'A' ? inputA : inputB;
    if (val.trim() === '') return;
    const parsed = parseCoords(val);
    if (!parsed) {
      if (which === 'A') setInputAError(true);
      else setInputBError(true);
    }
  };

  const handleGenerate = async () => {
    if (!pointA || !pointB) return;
    setIsLoading(true);
    setApiError(null);
    setGeneratedRoute(null);
    try {
      const response = await fetch('http://127.0.0.1:5000/api/generate-line', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          point_a: { lat: pointA.lat, lng: pointA.lng },
          point_b: { lat: pointB.lat, lng: pointB.lng },
        }),
      });
      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      const data = await response.json();
      // GeoJSON coordinates are [lng, lat]; Leaflet expects [lat, lng]
      const leafletCoords = data.geometry.coordinates.map(([lng, lat]) => [lat, lng]);
      setGeneratedRoute({ leaflet: leafletCoords, geojson: data });
    } catch (err) {
      console.error('Route generation failed:', err);
      setApiError('Could not reach server — showing preview route');
      // Fallback preview: straight line with a midpoint wobble
      const fallbackCoords = [
        [pointA.lat, pointA.lng],
        [(pointA.lat + pointB.lat) / 2 + 0.003, (pointA.lng + pointB.lng) / 2 - 0.004],
        [pointB.lat, pointB.lng],
      ];
      setGeneratedRoute({ leaflet: fallbackCoords, geojson: null });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = () => {
    if (!generatedRoute || !pointA || !pointB) return;
    const id = `L${routeCounterRef.current}`;
    const name = `Line ${routeCounterRef.current}`;
    routeCounterRef.current += 1;

    // Prefer saving the original GeoJSON feature from the server; fall back to synthetic coords
    const routeObj = generatedRoute.geojson
      ? { id, name, ...generatedRoute.geojson }
      : {
          id,
          name,
          type: 'Feature',
          properties: {},
          geometry: {
            type: 'LineString',
            // Convert back to GeoJSON [lng, lat] order for the saved file
            coordinates: generatedRoute.leaflet.map(([lat, lng]) => [lng, lat]),
          },
          meta: {
            pointA: { lat: pointA.lat, lng: pointA.lng },
            pointB: { lat: pointB.lat, lng: pointB.lng },
            savedAt: new Date().toISOString(),
          },
        };

    const blob = new Blob([JSON.stringify(routeObj, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${id}_route.json`;
    a.click();
    URL.revokeObjectURL(url);

    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2500);
  };

  const canGenerate = pointA && pointB && !isLoading;
  const canSave = !!generatedRoute;

  const cursorClass =
    selectingFor ? 'cursor-crosshair' : 'cursor-default';

  return (
    <div className={`relative h-screen w-screen overflow-hidden font-mono ${cursorClass}`}>

      {/* Full-bleed map */}
      <MapContainer
        center={[53.47941, -2.24464]}
        zoom={13}
        className="absolute inset-0 h-full w-full z-0"
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />
        <ClickHandler onMapClick={handleMapClick} />
        {pointA && <Marker position={pointA} icon={ICON_A} />}
        {pointB && <Marker position={pointB} icon={ICON_B} />}
        {generatedRoute && (
          <DirectionalPolyline
            positions={generatedRoute.leaflet}
            color={LINE_COLORS[0]}
            weight={5}
            opacity={0.85}
            arrowSpacing={8}
            stops={generatedRoute.geojson?.properties?.stops || null}
          />
        )}
      </MapContainer>

      {/* Floating panel — top right */}
      <div className="absolute top-4 right-4 z-10 w-72 flex flex-col gap-3">

        {/* Points card */}
        <div className="bg-white/90 backdrop-blur-md rounded-2xl shadow-xl border border-slate-200/60 p-5">

          <p className="text-[10px] font-semibold tracking-[0.18em] uppercase text-slate-400 mb-4">
            Route Builder
          </p>

          {/* Point A */}
          <div className="mb-3">
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                  <span className="text-[9px] font-bold text-white">A</span>
                </div>
                <span className="text-[10px] font-semibold tracking-widest uppercase text-slate-500">
                  Point A
                </span>
              </div>
              <button
                onClick={() => setSelectingFor(selectingFor === 'A' ? null : 'A')}
                className={`text-[9px] font-semibold tracking-widest uppercase px-2.5 py-1 rounded-lg border transition-all ${
                  selectingFor === 'A'
                    ? 'bg-blue-500 text-white border-blue-500'
                    : 'bg-white text-slate-500 border-slate-200 hover:border-blue-300 hover:text-blue-500'
                }`}
              >
                {selectingFor === 'A' ? 'Selecting…' : 'Pick on map'}
              </button>
            </div>
            <input
              type="text"
              placeholder="lat, lng  e.g. 53.797, -1.543"
              value={inputA}
              onChange={(e) => handleInputChange('A', e.target.value)}
              onBlur={() => handleInputBlur('A')}
              className={`w-full text-[11px] font-mono px-3 py-2 rounded-xl border bg-white/70 text-slate-700 placeholder:text-slate-300 focus:outline-none focus:ring-1 transition-all ${
                inputAError
                  ? 'border-red-300 focus:ring-red-300'
                  : 'border-slate-200 focus:ring-blue-300'
              }`}
            />
            {inputAError && (
              <p className="text-[9px] text-red-400 mt-1 tracking-wide">
                Invalid format — use: lat, lng
              </p>
            )}
          </div>

          {/* Divider */}
          <div className="flex items-center gap-2 my-2">
            <div className="flex-1 h-px bg-slate-100" />
            <div className="w-5 h-5 rounded-full border border-slate-200 flex items-center justify-center">
              <svg className="w-2.5 h-2.5 text-slate-300" viewBox="0 0 10 14" fill="none">
                <path d="M5 1v12M2 10l3 3 3-3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <div className="flex-1 h-px bg-slate-100" />
          </div>

          {/* Point B */}
          <div className="mb-1">
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 rounded-full bg-red-500 flex items-center justify-center">
                  <span className="text-[9px] font-bold text-white">B</span>
                </div>
                <span className="text-[10px] font-semibold tracking-widest uppercase text-slate-500">
                  Point B
                </span>
              </div>
              <button
                onClick={() => setSelectingFor(selectingFor === 'B' ? null : 'B')}
                className={`text-[9px] font-semibold tracking-widest uppercase px-2.5 py-1 rounded-lg border transition-all ${
                  selectingFor === 'B'
                    ? 'bg-red-500 text-white border-red-500'
                    : 'bg-white text-slate-500 border-slate-200 hover:border-red-300 hover:text-red-500'
                }`}
              >
                {selectingFor === 'B' ? 'Selecting…' : 'Pick on map'}
              </button>
            </div>
            <input
              type="text"
              placeholder="lat, lng  e.g. 53.805, -1.551"
              value={inputB}
              onChange={(e) => handleInputChange('B', e.target.value)}
              onBlur={() => handleInputBlur('B')}
              className={`w-full text-[11px] font-mono px-3 py-2 rounded-xl border bg-white/70 text-slate-700 placeholder:text-slate-300 focus:outline-none focus:ring-1 transition-all ${
                inputBError
                  ? 'border-red-300 focus:ring-red-300'
                  : 'border-slate-200 focus:ring-red-300'
              }`}
            />
            {inputBError && (
              <p className="text-[9px] text-red-400 mt-1 tracking-wide">
                Invalid format — use: lat, lng
              </p>
            )}
          </div>
        </div>

        {/* Error notice */}
        {apiError && (
          <div className="bg-amber-50/90 backdrop-blur-md rounded-2xl border border-amber-200/60 px-4 py-2.5">
            <p className="text-[9px] text-amber-600 tracking-wide">{apiError}</p>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex flex-col gap-2">
          <button
            onClick={handleGenerate}
            disabled={!canGenerate}
            className={`w-full py-3 px-4 text-xs font-semibold tracking-widest uppercase rounded-2xl shadow-lg transition-all flex items-center justify-center gap-2 ${
              canGenerate
                ? 'bg-slate-900/90 backdrop-blur-md hover:bg-slate-900 text-white'
                : 'bg-slate-100/90 text-slate-400 cursor-not-allowed shadow-none'
            }`}
          >
            {isLoading ? (
              <>
                <svg className="w-3 h-3 animate-spin" viewBox="0 0 16 16" fill="none">
                  <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="2" strokeDasharray="28" strokeDashoffset="10" />
                </svg>
                Generating…
              </>
            ) : (
              <>
                Generate
                <span className="text-slate-400">→</span>
              </>
            )}
          </button>

          <button
            onClick={handleSave}
            disabled={!canSave}
            className={`w-full py-3 px-4 text-xs font-semibold tracking-widest uppercase rounded-2xl border transition-all flex items-center justify-center gap-2 ${
              canSave
                ? saveSuccess
                  ? 'bg-emerald-50/90 backdrop-blur-md border-emerald-200/60 text-emerald-600 shadow-lg'
                  : 'bg-white/90 backdrop-blur-md border-slate-200/60 hover:bg-white hover:border-slate-300 text-slate-700 shadow-lg'
                : 'bg-white/50 border-slate-100 text-slate-300 cursor-not-allowed shadow-none'
            }`}
          >
            {saveSuccess ? (
              <>
                <svg className="w-3 h-3" viewBox="0 0 12 12" fill="none">
                  <path d="M1.5 6l3 3 6-6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Saved
              </>
            ) : (
              <>
                <svg className="w-3 h-3" viewBox="0 0 12 12" fill="none">
                  <path d="M6 1v7M3 5l3 3 3-3M1 10h10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Save Line
              </>
            )}
          </button>
        </div>

        {/* Hint when selecting */}
        {selectingFor && (
          <div className="bg-white/90 backdrop-blur-md rounded-2xl border border-slate-200/60 px-4 py-2.5 flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full animate-pulse ${selectingFor === 'A' ? 'bg-blue-400' : 'bg-red-400'}`} />
            <p className="text-[10px] text-slate-500 tracking-wide">
              Click the map to place point {selectingFor}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RouteBuilder;