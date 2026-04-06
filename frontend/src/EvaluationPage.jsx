import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const EvaluationPage = () => {
  const [stats, setStats] = useState({
    averageTime: null,
    averageNumBus: null,
    shortestJourneyTime: null,
    avgShortest10: null,
    longestJourneyTime: null,
    avgLongest10: null,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setIsLoading(true);
        const response = await fetch('/api/evaluation-stats'); // modify api endpoint
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        
        setStats({
          averageTime: data.average_time,
          averageNumBus: data.average_num_bus,
          shortestJourneyTime: data.shortest_journey_time,
          avgShortest10: data.avg_journey_time_shortest_10,
          longestJourneyTime: data.longest_journey_time,
          avgLongest10: data.avg_journey_time_longest_10,
        });
      } catch (err) {
        console.error("Failed to fetch stats:", err);
        setError(err.message);
        
        setStats({
          averageTime: '45 mins',
          averageNumBus: '2.4',
          shortestJourneyTime: '12 mins',
          avgShortest10: '15 mins',
          longestJourneyTime: '1h 20 mins',
          avgLongest10: '1h 10 mins',
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  const StatItem = ({ label, value }) => (
    <div className="flex flex-col border-b border-slate-100 pb-3 last:border-0">
      <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
        {label}
      </span>
      {isLoading ? (
        <div className="h-6 bg-slate-200 animate-pulse rounded w-24"></div>
      ) : (
        <span className="text-sm font-medium text-slate-700">
          {value !== null && value !== undefined ? value : 'N/A'}
        </span>
      )}
    </div>
  );

  return (
    <div className="flex h-screen w-screen bg-slate-50 font-sans overflow-hidden">

      <div className="flex-grow relative z-0">
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
        </MapContainer>
      </div>

      <div className="w-80 bg-white border-l-2 border-slate-300 shadow-xl p-6 flex flex-col overflow-y-auto z-10">
        <h2 className="text-lg font-bold text-slate-800 mb-6">Journey Statistics</h2>
        
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 text-xs rounded-lg">
            Failed to load live stats. Showing offline data.
          </div>
        )}

        <div className="flex flex-col space-y-4">
          <StatItem label="Average Time" value={stats.averageTime} />
          <StatItem label="Average Num Bus" value={stats.averageNumBus} />
          <StatItem label="Shortest Journey Time" value={stats.shortestJourneyTime} />
          <StatItem label="Avg Journey Time (Shortest 10%)" value={stats.avgShortest10} />
          <StatItem label="Longest Journey Time" value={stats.longestJourneyTime} />
          <StatItem label="Avg Journey Time (Longest 10%)" value={stats.avgLongest10} />
        </div>
      </div>
      
    </div>
  );
};

export default EvaluationPage;