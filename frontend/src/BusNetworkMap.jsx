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
  const [routeCounter, setRouteCounter] = useState(3);

  const toggleRouteVisibility = (id) => {
    setRoutes(routes.map(route => 
      route.id === id ? { ...route, visible: !route.visible } : route
    ));
  };

  const removeRoute = (id) => {
    setRoutes(routes.filter(route => route.id !== id));
  };

  const navigate=useNavigate();

  const handleEvaluation = () => {
    navigate('/evaluate'), { state: { activeRoutes: routes }};
  }



  return (
    <div className="flex h-screen w-screen bg-slate-50 font-sans overflow-hidden">
      
      <div className="flex-grow relative z-0">
        <MapContainer 
          center={[53.79725, -1.54384]} 
          zoom={13} 
          className="h-full w-full outline-none"
          zoomControl={true} 
        >
          <TileLayer
            attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          />
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

      <div className="w-72 bg-white border-l-2 border-slate-300 shadow-xl p-6 flex flex-col z-10">
        <h2 className="text-lg font-bold text-slate-800 mb-6">Active Routes</h2>
        
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
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: LINE_COLORS[index % LINE_COLORS.length] }}
                  />
                  <span className={`text-sm font-medium ${route.visible ? 'text-slate-700' : 'text-slate-400'}`}>
                    {route.name}
                  </span>
                </div>
              </label>
              
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

        <div className="pt-6 mt-4 border-t border-slate-100 flex flex-col gap-3">
          <button 
            //onClick={addRoute} // add way to process gpx file or coordinates for route
            className="w-full py-3 px-4 bg-white border-2 border-slate-300 hover:border-slate-400 hover:bg-slate-50 text-slate-700 font-semibold rounded-xl transition-all shadow-sm flex items-center justify-center gap-2"
          >
            <span className="text-lg leading-none">+</span>
            Add Route
          </button>
          
          <button 
            onClick={handleEvaluation} // will pass all active route as well
            className="w-full py-3 px-4 bg-slate-800 hover:bg-slate-900 text-white font-semibold rounded-xl transition-all shadow-sm flex items-center justify-center"
          >
            Evaluate
          </button>
        </div>
      </div>
      
    </div>
  );
};

export default BusNetworkMap;