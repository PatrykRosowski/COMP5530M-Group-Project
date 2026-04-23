import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Polyline, useMap } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import 'leaflet/dist/leaflet.css';

import NavBar from './Navbar';

const ROUTE_COLORS = ['#0891B2', '#2563EB', '#7C3AED', '#DB2777', '#EA580C', '#16A34A', '#DC2626'];

const INITIAL_ROUTES = [
  {
    id: 'L1',
    name: 'Line 1',
    visible: true,
    coordinates: [[53.47941, -2.24464], [53.48500, -2.25000], [53.49000, -2.25500]]
  }
];

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

const EyeIcon = ({ open }) => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    {open ? (
      <>
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
        <circle cx="12" cy="12" r="3" />
      </>
    ) : (
      <>
        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
        <line x1="1" y1="1" x2="23" y2="23" />
      </>
    )}
  </svg>
);

const PlusIcon = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
    <line x1="12" y1="5" x2="12" y2="19" />
    <line x1="5" y1="12" x2="19" y2="12" />
  </svg>
);

const ArrowRightIcon = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="5" y1="12" x2="19" y2="12" />
    <polyline points="12 5 19 12 12 19" />
  </svg>
);


const RouteTag = ({ color, label }) => (
  <span 
    className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold"
    style={{ 
      backgroundColor: `${color}15`,
      color: color,
      fontFamily: "'Fira Code', monospace"
    }}
  >
    {label}
  </span>
);

const BusNetworkMap = () => {
  const [routes, setRoutes] = useState([]);
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/routes')
      .then(res => {
        if (!res.ok) throw new Error('File not found');
        return res.json();
      })
      .then(data => setRoutes(data))
      .catch(() => setRoutes(INITIAL_ROUTES));
  }, []);

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

  const handleAddRouteClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target.result);
        
        // Format the route data for the map
        // Handle both direct coordinates and GeoJSON LineString
        let coordinates = [];
        if (json.geometry && json.geometry.type === 'LineString') {
          // GeoJSON uses [lng, lat], Leaflet uses [lat, lng]
          coordinates = json.geometry.coordinates.map(([lng, lat]) => [lat, lng]);
        } else if (json.coordinates) {
          coordinates = json.coordinates;
        }

        const newRoute = {
          id: json.id || `L${routes.length + 1}`,
          name: json.name || `Uploaded Line ${routes.length + 1}`,
          visible: true,
          coordinates: coordinates,
          properties: json.properties || {}
        };

        if (coordinates.length > 0) {
          setRoutes(prev => [...prev, newRoute]);
        } else {
          alert('Could not find valid coordinates in the JSON file.');
        }
      } catch (err) {
        console.error('Failed to parse route JSON:', err);
        alert('Invalid JSON file format.');
      }
    };
    reader.readAsText(file);
    // Reset input value so the same file can be uploaded again
    event.target.value = '';
  };

  return (
    <div className="relative h-screen w-screen overflow-hidden bg-[#E2E8F0]">
      <NavBar className="absolute top-5 left-5 z-20 w-80" />
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        accept=".json"
        className="hidden"
      />
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
        {routes.filter(r => r.visible).map((route, index) => (
          <Polyline
            key={`route-${route.id}-${index}`}
            positions={route.coordinates}
            pathOptions={{
              color: ROUTE_COLORS[index % ROUTE_COLORS.length],
              weight: 5,
              opacity: 0.85,
            }}
          />
        ))}
      </MapContainer>

      <div className="absolute bottom-0 left-0 right-0 z-10 sm:absolute sm:top-[calc(5rem+1rem)] sm:right-5 sm:bottom-auto sm:w-80 flex flex-col gap-4 p-4 sm:p-0 ml-5">
        <div className="bg-white rounded-2xl shadow-lg shadow-slate-200/50 p-5 border border-slate-100 max-h-[60vh] overflow-y-auto">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">Active Routes</h3>
          
          <div className="flex flex-col gap-1.5">
            {routes.length === 0 && (
              <div className="py-8 text-center">
                <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-3">
                  <svg className="w-6 h-6 text-slate-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M8 12h8M12 8v8"/>
                  </svg>
                </div>
                <p className="text-sm text-slate-400">No routes loaded</p>
                <p className="text-xs text-slate-300 mt-1">Add routes to see them here</p>
              </div>
            )}

            {routes.map((route, index) => (
              <div
                key={`${route.id}-${index}`}
                className="group flex items-center justify-between py-3 px-4 rounded-xl hover:bg-slate-50 transition-all duration-200 border border-transparent hover:border-slate-100"
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-3 h-3 rounded-full flex-shrink-0 shadow-sm"
                    style={{
                      backgroundColor: ROUTE_COLORS[index % ROUTE_COLORS.length],
                    }}
                  />
                  <div className="flex flex-col">
                    <span className={`text-sm font-medium transition-colors duration-200 ${route.visible ? 'text-slate-700' : 'text-slate-400'}`}>
                      {route.name}
                    </span>
                    <RouteTag 
                      color={ROUTE_COLORS[index % ROUTE_COLORS.length]} 
                      label={route.id} 
                    />
                  </div>
                </div>

                <div className="flex items-center gap-1.5 opacity-80 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => toggleRouteVisibility(route.id)}
                    className={`p-2 rounded-lg transition-all duration-200 cursor-pointer ${
                      route.visible
                        ? 'text-cyan-600 hover:bg-cyan-50'
                        : 'text-slate-300 hover:text-slate-500 hover:bg-slate-100'
                    }`}
                    title={route.visible ? 'Hide route' : 'Show route'}
                  >
                    <EyeIcon open={route.visible} />
                  </button>
                  <button
                    onClick={() => removeRoute(route.id)}
                    className="p-2 rounded-lg text-slate-300 hover:text-red-500 hover:bg-red-50 transition-all duration-200 cursor-pointer"
                    title="Remove Route"
                  >
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                      <line x1="18" y1="6" x2="6" y2="18" />
                      <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-2.5">
          <button 
            onClick={handleAddRouteClick}
            className="w-full py-3 px-4 bg-white hover:bg-slate-50 text-slate-600 border-2 border-slate-200 hover:border-cyan-300 hover:text-cyan-600 text-sm font-semibold rounded-xl shadow-sm transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer"
          >
            <PlusIcon />
            Add Route
          </button>

          <button
            onClick={handleEvaluation}
            className="w-full py-3 px-4 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white text-sm font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer"
          >
            Evaluate Network
            <ArrowRightIcon />
          </button>
        </div>
      </div>
    </div>
  );
};

export default BusNetworkMap;