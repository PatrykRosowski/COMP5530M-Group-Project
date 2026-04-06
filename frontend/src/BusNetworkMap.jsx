import React, { useState } from 'react';
import { MapContainer, TileLayer, Polyline } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import 'leaflet/dist/leaflet.css';

const LINE_COLORS = ['#ef4444', '#3b82f6', '#22c55e', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4'];

const INITIAL_ROUTES = [
  {
    id: 'L1',
    name: 'Line 1',
    visible: true,
    coordinates: [[53.79725, -1.54384], [53.80100, -1.54800], [53.80500, -1.55200]]
  },
  {
    id: 'L2',
    name: 'Line 2',
    visible: true,
    coordinates: [[53.79725, -1.54384], [53.79200, -1.54000], [53.78800, -1.53500]]
  }
];

const BusNetworkMap = () => {
  const [routes, setRoutes] = useState(INITIAL_ROUTES);
  const navigate = useNavigate();

  const toggleRouteVisibility = (id) => {
    setRoutes(routes.map(route =>
      route.id === id ? { ...route, visible: !route.visible } : route
    ));
  };

  const removeRoute = (id) => {
    setRoutes(routes.filter(route => route.id !== id));
  };

  const handleEvaluation = () => {
    navigate('/evaluate', { state: { activeRoutes: routes } });
  };

  return (
    <div className="relative h-screen w-screen overflow-hidden font-mono">

      {/* Full-bleed map */}
      <MapContainer
        center={[53.79725, -1.54384]}
        zoom={13}
        className="absolute inset-0 h-full w-full z-0"
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />
        {routes.filter(r => r.visible).map((route, index) => (
          <Polyline
            key={`route-${route.id}`}
            positions={route.coordinates}
            pathOptions={{
              color: LINE_COLORS[index % LINE_COLORS.length],
              weight: 5,
              opacity: 0.85,
            }}
          />
        ))}
      </MapContainer>

      {/* Floating panel — top right */}
      <div className="absolute top-4 right-4 z-10 w-72 flex flex-col gap-3">

        {/* Routes card */}
        <div className="bg-white/90 backdrop-blur-md rounded-2xl shadow-xl border border-slate-200/60 p-5">
          <p className="text-[10px] font-semibold tracking-[0.18em] uppercase text-slate-400 mb-4">
            Active Routes
          </p>

          <div className="flex flex-col gap-2">
            {routes.length === 0 && (
              <p className="text-xs text-slate-400 italic">No routes loaded.</p>
            )}

            {routes.map((route, index) => (
              <div key={route.id} className="flex items-center justify-between group">
                <label className="flex items-center gap-3 cursor-pointer flex-1 min-w-0" onClick={() => toggleRouteVisibility(route.id)}>
                  <div
                    className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-all flex-shrink-0
                      ${route.visible ? 'border-transparent' : 'border-slate-300 bg-white'}`}
                    style={route.visible ? { backgroundColor: LINE_COLORS[index % LINE_COLORS.length] } : {}}
                  >
                    {route.visible && (
                      <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 10 10">
                        <path d="M1.5 5l2.5 2.5 4.5-4.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    )}
                  </div>

                  <div className="flex items-center gap-2 min-w-0">
                    <div
                      className="w-2 h-5 rounded-full flex-shrink-0"
                      style={{ backgroundColor: LINE_COLORS[index % LINE_COLORS.length], opacity: route.visible ? 1 : 0.3 }}
                    />
                    <span className={`text-xs font-medium truncate transition-colors ${route.visible ? 'text-slate-700' : 'text-slate-400'}`}>
                      {route.name}
                    </span>
                  </div>
                </label>

                <button
                  onClick={() => removeRoute(route.id)}
                  className="ml-2 w-6 h-6 flex items-center justify-center rounded-full text-slate-300 hover:text-red-400 hover:bg-red-50 transition-all text-xs flex-shrink-0"
                  title="Remove Route"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Action buttons card */}
        <div className="flex flex-col gap-2">
          <button
            className="w-full py-3 px-4 bg-white/90 backdrop-blur-md border border-slate-200/60 hover:bg-white hover:border-slate-300 text-slate-700 text-xs font-semibold tracking-wide rounded-2xl shadow-lg transition-all flex items-center justify-center gap-2"
          >
            <span className="text-base leading-none">+</span>
            Add Route
          </button>

          <button
            onClick={handleEvaluation}
            className="w-full py-3 px-4 bg-slate-900/90 backdrop-blur-md hover:bg-slate-900 text-white text-xs font-semibold tracking-widest uppercase rounded-2xl shadow-lg transition-all flex items-center justify-center gap-2"
          >
            Evaluate
            <span className="text-slate-400">→</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default BusNetworkMap;