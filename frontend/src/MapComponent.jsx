import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import axios from 'axios';
import 'leaflet/dist/leaflet.css';

const MapComponent = () => {
  const [apiData, setApiData] = useState({ 
    lines: [], 
    latency: null 
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/generate-line');
        setApiData(response.data);
      } catch (error) {
        console.error("Error fetching routes:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getLineStyle = (index) => {
    const colors = ['#ef4444', '#3b82f6', '#22c55e', '#f59e0b', '#8b5cf6'];
    return {
      color: colors[index % colors.length],
      weight: 5,
      opacity: 0.8,
    };
  };

  return (
    <div className="relative h-screen w-screen bg-slate-50 overflow-hidden">
      
      <div className="absolute top-6 left-1/2 transform -translate-x-1/2 z-1000">
        <div className="bg-white/90 backdrop-blur-sm shadow-lg border border-slate-200 rounded-full px-6 py-3 flex items-center gap-4 transition-all">
          
          {loading ? (
            <div className="flex items-center gap-2 text-slate-600 text-sm font-medium">
               <svg className="animate-spin h-5 w-5 text-slate-500" viewBox="0 0 24 24">
                   <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                   <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
               </svg>
               <span>Optimizing Network...</span>
            </div>
          ) : (
             apiData.latency && (
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">Max Latency</span>
                  <div className="h-4 w-px bg-slate-300"></div> {/* Separator */}
                  <span className="text-emerald-600 font-mono text-lg font-bold leading-none">
                    {apiData.latency.toFixed(2)}s
                  </span>
                </div>
             )
          )}
        </div>
      </div>

      <div className="absolute inset-0 z-0">
        <MapContainer 
          center={[53.79725, -1.54384]} 
          zoom={15} 
          className="h-full w-full outline-none"
          zoomControl={false} // Optional: removes zoom +/- buttons for a cleaner look
        >
          <TileLayer
            attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          />

          {!loading && apiData.lines && apiData.lines.map((lineGeoJson, index) => (
            <GeoJSON 
              key={`line-${index}`} 
              data={lineGeoJson} 
              style={getLineStyle(index)}
              onEachFeature={(feature, layer) => {
                if (feature.properties?.order) {
                  layer.bindPopup(`
                    <div style="font-family: system-ui;">
                      <strong style="color: #334155;">Line ${index + 1}</strong><br/>
                      <span style="color: #64748b;">${feature.properties.order.length} Stops</span>
                    </div>
                  `);
                }
              }}
            />
          ))}
        </MapContainer>
      </div>
    </div>
  );
};

export default MapComponent;