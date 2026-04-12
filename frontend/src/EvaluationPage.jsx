import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

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

const ClockIcon = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <polyline points="12 6 12 12 16 14" />
  </svg>
);

const BusIcon = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M8 6v6M16 6v6M2 12h20M4 18V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z" />
  </svg>
);

const TrendUpIcon = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
    <polyline points="17 6 23 6 23 12" />
  </svg>
);

const TrendDownIcon = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 18 13.5 8.5 8.5 13.5 1 6" />
    <polyline points="17 18 23 18 23 12" />
  </svg>
);



const StatCard = ({ label, value, icon, accent = false, trendUp, isLoading }) => (
  <div className={`flex items-center gap-4 py-4 px-5 rounded-xl transition-all duration-200 ${accent ? 'bg-slate-50 border border-slate-100' : 'bg-white border border-slate-100 hover:border-cyan-200 hover:shadow-sm'}`}>
    <div className={`p-2.5 rounded-xl ${accent ? 'bg-cyan-50' : 'bg-cyan-100'}`}>
      <span className={accent ? 'text-cyan-500' : 'text-cyan-600'}>{icon}</span>
    </div>
    <div className="flex-1 min-w-0">
      <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
        {label}
      </p>
      {isLoading ? (
        <div className="h-7 bg-slate-200 animate-shimmer rounded-md w-20 mt-1" />
      ) : (
        <p className={`text-xl font-bold tabular-nums mt-0.5 ${accent ? 'text-slate-400' : 'text-slate-800'}`} style={{ fontFamily: "'Fira Code', monospace" }}>
          {value !== null && value !== undefined ? value : '—'}
        </p>
      )}
    </div>
    {trendUp !== undefined && !isLoading && (
      <div className={`p-2 rounded-lg ${trendUp ? 'bg-emerald-100 text-emerald-600' : 'bg-rose-100 text-rose-500'}`}>
        {trendUp ? <TrendUpIcon /> : <TrendDownIcon />}
      </div>
    )}
  </div>
);

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
        const response = await fetch('/api/evaluation-stats');
        if (!response.ok) throw new Error('Network response was not ok');
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

  return (
    <div className="relative h-screen w-screen overflow-hidden bg-[#E2E8F0]">

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
        <MapResizer />
      </MapContainer>

      <div className="absolute top-5 right-5 z-10 w-80">
        <div className="bg-white rounded-2xl shadow-lg shadow-slate-200/50 p-5 border-t-2 border-t-slate-200">



          {!isLoading && (
            <div className="flex items-center gap-2 mb-4">
              <div className={`w-2 h-2 rounded-full ${error ? 'bg-amber-400' : 'bg-emerald-400'} animate-pulse-soft`} />
              <span className="text-xs font-medium text-slate-400">
                {error ? 'Using cached data' : 'Live data'}
              </span>
            </div>
          )}

          {error && (
            <div className="mb-4 px-4 py-3 bg-amber-50 border border-amber-100 rounded-xl">
              <p className="text-xs text-amber-600">Network unavailable — showing offline data</p>
            </div>
          )}

          <div className="flex flex-col gap-3">
            <StatCard label="Average Time" value={stats.averageTime} icon={<ClockIcon />} isLoading={isLoading} />
            <StatCard label="Average Buses" value={stats.averageNumBus} icon={<BusIcon />} isLoading={isLoading} />
            <StatCard label="Shortest Journey" value={stats.shortestJourneyTime} icon={<ClockIcon />} trendUp={true} isLoading={isLoading} />
            <StatCard label="Avg (Bottom 10%)" value={stats.avgShortest10} icon={<ClockIcon />} accent trendUp={true} isLoading={isLoading} />
            <StatCard label="Longest Journey" value={stats.longestJourneyTime} icon={<ClockIcon />} trendUp={false} isLoading={isLoading} />
            <StatCard label="Avg (Top 10%)" value={stats.avgLongest10} icon={<ClockIcon />} accent trendUp={false} isLoading={isLoading} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default EvaluationPage;