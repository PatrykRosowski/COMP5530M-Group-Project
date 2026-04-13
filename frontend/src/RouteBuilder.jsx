import React, { useState, useCallback, useRef } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, useMap, useMapEvents, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const ROUTE_COLORS = ['#0891B2', '#2563EB', '#7C3AED', '#DB2777', '#EA580C', '#16A34A', '#DC2626'];

const makeIcon = (label, color) =>
  L.divIcon({
    className: '',
    html: `<div style="
      width:30px;height:30px;border-radius:50%;
      background:${color};border:3px solid white;
      box-shadow:0 2px 8px rgba(0,0,0,0.15);
      display:flex;align-items:center;justify-content:center;
      font-size:11px;font-weight:700;color:white;
      font-family:'Fira Code',monospace;
    ">${label}</div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
  });

const makeArrowIcon = (color, rotation) =>
  L.divIcon({
    className: '',
    html: `<svg width="16" height="16" viewBox="0 0 16 16" style="transform: rotate(${rotation}deg);">
      <polygon points="8,0 16,14 0,14" fill="${color}"/>
    </svg>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });

const makeStopIcon = (index) =>
  L.divIcon({
    className: '',
    html: `<div style="
      width:20px;height:20px;border-radius:50%;
      background:#0891B2;border:2.5px solid white;
      box-shadow:0 1px 4px rgba(0,0,0,0.15);
      display:flex;align-items:center;justify-content:center;
      font-size:8px;font-weight:600;color:white;
      font-family:'Fira Code',monospace;
    ">${index + 1}</div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
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
            <span style={{ fontFamily: "'Fira Code', monospace", fontSize: '11px' }}>{stop.name}</span>
            {stop.street && (
              <span style={{ fontSize: '10px', color: '#64748B', display: 'block', marginTop: '2px' }}>{stop.street}</span>
            )}
          </Tooltip>
        </Marker>
      ))
    : null;

  return (
    <>
      <Polyline positions={positions} pathOptions={{ color, weight, opacity, shadowBlur: 6, shadowColor: color + '50' }} />
      {arrowMarkers}
      {stopMarkers}
    </>
  );
};

const ICON_A = makeIcon('A', '#0891B2');
const ICON_B = makeIcon('B', '#DC2626');

const MapResizer = () => {
  const map = useMap();
  React.useEffect(() => {
    const handleResize = () => map.invalidateSize();
    window.addEventListener('resize', handleResize);
    document.addEventListener('fullscreenchange', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      document.removeEventListener('fullscreenchange', handleResize);
    };
  }, [map]);
  return null;
};

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

const MapPinIcon = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
    <circle cx="12" cy="10" r="3" />
  </svg>
);

const RouteBuilder = () => {
  const [selectingFor, setSelectingFor] = useState(null);
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
      const leafletCoords = data.geometry.coordinates.map(([lng, lat]) => [lat, lng]);
      setGeneratedRoute({ leaflet: leafletCoords, geojson: data });
    } catch (err) {
      console.error('Route generation failed:', err);
      setApiError('Could not reach server — showing preview route');
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

    const routeObj = generatedRoute.geojson
      ? { id, name, ...generatedRoute.geojson }
      : {
          id,
          name,
          type: 'Feature',
          properties: {},
          geometry: {
            type: 'LineString',
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

  const cursorClass = selectingFor ? 'cursor-crosshair' : 'cursor-default';

  return (
    <div className={`relative h-screen w-screen overflow-hidden bg-[#E2E8F0] ${cursorClass}`}>

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
        <MapResizer />
        <ClickHandler onMapClick={handleMapClick} />
        {pointA && <Marker position={pointA} icon={ICON_A} />}
        {pointB && <Marker position={pointB} icon={ICON_B} />}
        {generatedRoute && (
          <DirectionalPolyline
            positions={generatedRoute.leaflet}
            color={ROUTE_COLORS[0]}
            weight={5}
            opacity={0.85}
            arrowSpacing={8}
            stops={generatedRoute.geojson?.properties?.stops || null}
          />
        )}
      </MapContainer>

      <div className="absolute bottom-0 left-0 right-0 z-10 sm:absolute sm:top-5 sm:right-5 sm:bottom-auto sm:w-80 flex flex-col gap-4 p-4 sm:p-0 ml-5">
        <div className="bg-white rounded-2xl shadow-lg shadow-slate-200/50 p-5 border-t-2 border-t-slate-200 max-h-[50vh] sm:max-h-none overflow-y-auto">


          <div className="grid grid-cols-2 gap-4 mb-5">
            <div className="group">
              <div className="flex items-center gap-2 mb-2.5">
                <div className="w-6 h-6 rounded-full bg-cyan-100 flex items-center justify-center">
                  <span className="text-[10px] font-bold text-cyan-600" style={{ fontFamily: "'Fira Code', monospace" }}>A</span>
                </div>
                <span className="text-xs font-medium text-slate-500 uppercase tracking-wide">Origin</span>
              </div>
              <input
                type="text"
                placeholder="53.797, -1.543"
                value={inputA}
                onChange={(e) => handleInputChange('A', e.target.value)}
                onBlur={() => handleInputBlur('A')}
                className={`w-full text-sm px-3 py-2.5 bg-slate-50 border-2 ${inputAError ? 'border-red-300 bg-red-50' : 'border-slate-200 focus:border-cyan-400'} rounded-xl text-slate-700 placeholder:text-slate-300 focus:outline-none transition-all`}
                style={{ fontFamily: "'Fira Code', monospace" }}
              />
              <button
                onClick={() => setSelectingFor(selectingFor === 'A' ? null : 'A')}
                className={`mt-2 w-full text-xs py-2 rounded-xl transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                  selectingFor === 'A'
                    ? 'bg-cyan-100 text-cyan-700 border border-cyan-300'
                    : 'bg-slate-100 text-slate-500 hover:bg-slate-150 border border-transparent hover:border-slate-200'
                }`}
              >
                <MapPinIcon />
                {selectingFor === 'A' ? 'Cancel' : 'Pick on map'}
              </button>
            </div>

            <div className="group">
              <div className="flex items-center gap-2 mb-2.5">
                <div className="w-6 h-6 rounded-full bg-red-100 flex items-center justify-center">
                  <span className="text-[10px] font-bold text-red-500" style={{ fontFamily: "'Fira Code', monospace" }}>B</span>
                </div>
                <span className="text-xs font-medium text-slate-500 uppercase tracking-wide">Destination</span>
              </div>
              <input
                type="text"
                placeholder="53.805, -1.551"
                value={inputB}
                onChange={(e) => handleInputChange('B', e.target.value)}
                onBlur={() => handleInputBlur('B')}
                className={`w-full text-sm px-3 py-2.5 bg-slate-50 border-2 ${inputBError ? 'border-red-300 bg-red-50' : 'border-slate-200 focus:border-cyan-400'} rounded-xl text-slate-700 placeholder:text-slate-300 focus:outline-none transition-all`}
                style={{ fontFamily: "'Fira Code', monospace" }}
              />
              <button
                onClick={() => setSelectingFor(selectingFor === 'B' ? null : 'B')}
                className={`mt-2 w-full text-xs py-2 rounded-xl transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                  selectingFor === 'B'
                    ? 'bg-cyan-100 text-cyan-700 border border-cyan-300'
                    : 'bg-slate-100 text-slate-500 hover:bg-slate-150 border border-transparent hover:border-slate-200'
                }`}
              >
                <MapPinIcon />
                {selectingFor === 'B' ? 'Cancel' : 'Pick on map'}
              </button>
            </div>
          </div>

          {inputAError && <p className="text-[11px] text-red-500 mb-3">Invalid format — use: lat, lng</p>}
          {inputBError && <p className="text-[11px] text-red-500 mb-3">Invalid format — use: lat, lng</p>}

          <div className="flex flex-col gap-2.5">
            <button
              onClick={handleGenerate}
              disabled={!canGenerate}
              className={`w-full py-3 px-4 text-sm font-semibold rounded-xl transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer ${
                canGenerate
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white shadow-md hover:shadow-lg'
                  : 'bg-slate-200 text-slate-400 cursor-not-allowed'
              }`}
            >
              {isLoading ? (
                <>
                  <svg className="w-4 h-4 animate-spin" viewBox="0 0 16 16" fill="none">
                    <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="2" strokeDasharray="28" strokeDashoffset="10" />
                  </svg>
                  Generating route...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                  </svg>
                  Generate Route
                </>
              )}
            </button>

            <button
              onClick={handleSave}
              disabled={!canSave}
              className={`w-full py-3 px-4 text-sm font-semibold rounded-xl transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer ${
                canSave
                  ? saveSuccess
                    ? 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                    : 'bg-white text-slate-600 border-2 border-slate-200 hover:border-cyan-400 hover:text-cyan-600'
                  : 'bg-slate-100 text-slate-400 border border-transparent cursor-not-allowed'
              }`}
            >
              {saveSuccess ? (
                <>
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                  Route Saved
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                    <polyline points="17 21 17 13 7 13 7 21"/>
                    <polyline points="7 3 7 8 15 8"/>
                  </svg>
                  Save Line
                </>
              )}
            </button>
          </div>
        </div>

        {apiError && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 flex items-center gap-3">
            <svg className="w-5 h-5 text-amber-500 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <p className="text-xs text-amber-700">{apiError}</p>
          </div>
        )}

        {selectingFor && (
          <div className="bg-white border border-cyan-200 rounded-xl px-4 py-3 flex items-center gap-3 shadow-md">
            <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse-soft" />
            <p className="text-sm text-slate-600 font-medium">
              Click on map to place point <span className="text-cyan-600 font-bold" style={{ fontFamily: "'Fira Code', monospace" }}>{selectingFor}</span>
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RouteBuilder;