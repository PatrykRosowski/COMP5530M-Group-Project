import React, { useState } from 'react';
import { MapContainer, TileLayer, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Pre-defined colors for the bus lines
const LINE_COLORS = ['#ef4444', '#3b82f6', '#22c55e', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4'];

// Initial dummy data
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
  const [routeCounter, setRouteCounter] = useState(3);

  // Toggle whether a route is drawn on the map
  const toggleRouteVisibility = (id) => {
    setRoutes(routes.map(route => 
      route.id === id ? { ...route, visible: !route.visible } : route
    ));
  };

  // Completely remove a route from the list and map
  const removeRoute = (id) => {
    setRoutes(routes.filter(route => route.id !== id));
  };

  // Simulate fetching or generating a new route
  const addRoute = () => {
    // Generate some random coordinates around Leeds for the demo
    const baseLat = 53.79 + (Math.random() * 0.04 - 0.02);
    const baseLon = -1.54 + (Math.random() * 0.04 - 0.02);
    
    const newRoute = {
      id: `L${routeCounter}`,
      name: `Line ${routeCounter}`,
      visible: true,
      coordinates: [
        [baseLat, baseLon],
        [baseLat + (Math.random() * 0.02), baseLon + (Math.random() * 0.02)],
        [baseLat + (Math.random() * 0.04), baseLon - (Math.random() * 0.02)]
      ]
    };

    setRoutes([...routes, newRoute]);
    setRouteCounter(prev => prev + 1);
  };

  return (
    // Outer container matching the wireframe layout
    <div className="flex h-screen w-screen p-6 gap-6 bg-slate-50 font-sans">
      
      {/* LEFT: Map Area */}
      <div className="flex-grow rounded-2xl overflow-hidden border-2 border-slate-300 shadow-sm relative">
        <MapContainer 
          center={[53.79725, -1.54384]} 
          zoom={13} 
          className="h-full w-full outline-none z-0"
          zoomControl={true} 
        >
          <TileLayer
            attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          />

          {/* Render only visible lines */}
          {routes.filter(route => route.visible).map((route, index) => (
            <Polyline 
              key={`route-${route.id}`} 
              positions={route.coordinates} 
              pathOptions={{
                color: LINE_COLORS[index % LINE_COLORS.length],
                weight: 5,
                opacity: 0.8,
              }}
            />
          ))}
        </MapContainer>
      </div>

      {/* RIGHT: Control Panel */}
      <div className="w-72 bg-white rounded-2xl border-2 border-slate-300 shadow-sm p-6 flex flex-col">
        <h2 className="text-lg font-bold text-slate-800 mb-6">Active Routes</h2>
        
        {/* Route List */}
        <div className="flex-grow overflow-y-auto space-y-3 pr-2">
          {routes.length === 0 && (
            <p className="text-sm text-slate-400 italic">No routes loaded.</p>
          )}
          
          {routes.map((route, index) => (
            <div key={route.id} className="flex items-center justify-between group">
              <label className="flex items-center gap-3 cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={route.visible}
                  onChange={() => toggleRouteVisibility(route.id)}
                  className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                />
                <div className="flex items-center gap-2">
                  {/* Color Swatch */}
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: LINE_COLORS[index % LINE_COLORS.length] }}
                  />
                  <span className={`text-sm font-medium ${route.visible ? 'text-slate-700' : 'text-slate-400'}`}>
                    {route.name}
                  </span>
                </div>
              </label>
              
              {/* Remove Button */}
              <button 
                onClick={() => removeRoute(route.id)}
                className="text-slate-300 hover:text-red-500 transition-colors px-2 py-1 text-xs font-bold rounded"
                title="Remove Route"
              >
                ✕
              </button>
            </div>
          ))}
        </div>

        {/* Add Route Button */}
        <div className="pt-6 mt-4 border-t border-slate-100">
          <button 
            onClick={addRoute}
            className="w-full py-3 px-4 bg-white border-2 border-slate-300 hover:border-slate-400 hover:bg-slate-50 text-slate-700 font-semibold rounded-xl transition-all shadow-sm flex items-center justify-center gap-2"
          >
            <span className="text-lg leading-none">+</span>
            Add Route
          </button>
        </div>
      </div>
      
    </div>
  );
};

export default BusNetworkMap;