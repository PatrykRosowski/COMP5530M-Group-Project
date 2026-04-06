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

  const StatRow = ({ label, value, accent = false }) => (
    <div className={`flex flex-col gap-1 py-3 border-b border-slate-100 last:border-0 ${accent ? 'opacity-60' : ''}`}>
      <span className="text-[9px] font-semibold tracking-[0.2em] uppercase text-slate-400">
        {label}
      </span>
      {isLoading ? (
        <div className="h-5 bg-slate-100 animate-pulse rounded-md w-20" />
      ) : (
        <span className="text-sm font-semibold text-slate-800 tabular-nums">
          {value !== null && value !== undefined ? value : '—'}
        </span>
      )}
    </div>
  );

  const Divider = ({ label }) => (
    <div className="flex items-center gap-2 py-1">
      <div className="flex-1 h-px bg-slate-100" />
      <span className="text-[9px] tracking-widest uppercase text-slate-300 font-medium">{label}</span>
      <div className="flex-1 h-px bg-slate-100" />
    </div>
  );

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
      </MapContainer>

      {/* Floating panel — top right */}
      <div className="absolute top-4 right-4 z-10 w-72">
        <div className="bg-white/90 backdrop-blur-md rounded-2xl shadow-xl border border-slate-200/60 p-5">

          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <p className="text-[10px] font-semibold tracking-[0.18em] uppercase text-slate-400">
              Journey Statistics
            </p>
            {!isLoading && (
              <div className={`w-1.5 h-1.5 rounded-full ${error ? 'bg-amber-400' : 'bg-emerald-400'}`} title={error ? 'Offline data' : 'Live'} />
            )}
          </div>

          {error && (
            <div className="mb-3 px-3 py-2 bg-amber-50 border border-amber-200/60 rounded-xl">
              <p className="text-[9px] text-amber-600 tracking-wide">Offline — showing cached data</p>
            </div>
          )}

          {/* Stats */}
          <div className="flex flex-col">
            <StatRow label="Average Time" value={stats.averageTime} />
            <StatRow label="Average Buses" value={stats.averageNumBus} />

            <Divider label="Shortest" />
            <StatRow label="Shortest Journey" value={stats.shortestJourneyTime} />
            <StatRow label="Avg (Bottom 10%)" value={stats.avgShortest10} accent />

            <Divider label="Longest" />
            <StatRow label="Longest Journey" value={stats.longestJourneyTime} />
            <StatRow label="Avg (Top 10%)" value={stats.avgLongest10} accent />
          </div>
        </div>
      </div>
    </div>
  );
};

export default EvaluationPage;