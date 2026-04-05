import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polyline, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Pre-defined colors for the bus lines to match the legend
const LINE_COLORS = ['#ef4444', '#3b82f6', '#22c55e', '#f59e0b', '#8b5cf6'];

const BusNetworkMap = ({ 
  // Accept routes and stops as props, or fall back to an empty array
  routes = [], 
  stops = [] 
}) => {
  const [loading, setLoading] = useState(true);

  // Simulate a brief loading state to show off the HUD, 
  // or use this block to actually format your incoming coordinate data.
  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1200);
    return () => clearTimeout(timer);
  }, [routes, stops]);

  const getLineStyle = (index) => {
    return {
      color: LINE_COLORS[index % LINE_COLORS.length],
      weight: 5,
      opacity: 0.8,
    };
  };

  // Center on the first stop, or default to Leeds coordinates
  const mapCenter = stops.length > 0 ? [stops[0].lat, stops[0].lon] : [53.79725, -1.54384];

  return (
    <div className="relative h-screen w-screen bg-slate-50 overflow-hidden">
      
      {/* HUD / Status Bar */}
      <div className="absolute top-6 left-1/2 transform -translate-x-1/2 z-[1000]">
        <div className="bg-white/90 backdrop-blur-sm shadow-lg border border-slate-200 rounded-full px-6 py-3 flex items-center gap-4 transition-all">
          {loading ? (
            <div className="flex items-center gap-2 text-slate-600 text-sm font-medium">
               <svg className="animate-spin h-5 w-5 text-slate-500" viewBox="0 0 24 24">
                   <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                   <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
               </svg>
               <span>Mapping Coordinates...</span>
            </div>
          ) : (
             <div className="flex items-center gap-3">
               <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">Network Status</span>
               <div className="h-4 w-px bg-slate-300"></div>
               <span className="text-emerald-600 font-mono text-sm font-bold leading-none">
                 {routes.length} Active Lines
               </span>
             </div>
          )}
        </div>
      </div>

      {/* LEGEND COMPONENT */}
      {!loading && routes.length > 0 && (
        <div className="absolute bottom-8 right-8 z-[1000]">
          <div className="bg-white/90 backdrop-blur-sm shadow-lg border border-slate-200 rounded-xl p-4 min-w-[200px]">
            <h3 className="text-xs font-bold text-slate-400 uppercase mb-3 tracking-wider border-b border-slate-100 pb-2">
              Network Legend
            </h3>
            <div className="space-y-3">
              {routes.map((route, index) => (
                <div key={`legend-${route.id || index}`} className="flex items-center gap-3">
                  {/* Color Swatch */}
                  <div 
                    className="h-1.5 w-8 rounded-full shadow-sm" 
                    style={{ backgroundColor: LINE_COLORS[index % LINE_COLORS.length] }}
                  ></div>
                  {/* Label */}
                  <span className="text-sm font-semibold text-slate-700">
                    {route.name || `Bus Line ${index + 1}`}
                  </span>
                </div>
              ))}
              
              {/* Stop Legend Item */}
              <div className="flex items-center gap-3 pt-2">
                 <div className="h-3 w-3 rounded-full bg-white border-[2px] border-slate-600 shadow-sm mx-2.5"></div>
                 <span className="text-sm font-medium text-slate-500">Bus Stop</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="absolute inset-0 z-0">
        <MapContainer 
          center={mapCenter} 
          zoom={14} 
          className="h-full w-full outline-none"
          zoomControl={false} 
        >
          <TileLayer
            attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          />

          {/* Render Lines from Coordinate Arrays */}
          {!loading && routes.map((route, index) => (
            <Polyline 
              key={`route-${route.id || index}`} 
              positions={route.coordinates} 
              pathOptions={getLineStyle(index)}
            />
          ))}

          {/* Render Stops */}
          {!loading && stops.map((stop, index) => (
            <CircleMarker
              key={stop.id || index}
              center={[stop.lat, stop.lon]}
              radius={5}
              pathOptions={{ 
                color: '#475569',
                fillColor: '#ffffff',
                fillOpacity: 1,
                weight: 2
              }}
            >
              <Popup>
                <div className="font-sans p-1">
                  <div className="font-bold text-slate-700 text-sm">{stop.name}</div>
                  {stop.id && <div className="text-xs text-slate-400">Stop ID: {stop.id}</div>}
                </div>
              </Popup>
            </CircleMarker>
          ))}

        </MapContainer>
      </div>
    </div>
  );
};

export default BusNetworkMap;