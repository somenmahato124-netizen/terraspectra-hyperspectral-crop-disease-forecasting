import React, { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN;

export default function App() {
  const mapContainer = useRef(null);
  const map = useRef(null);

  useEffect(() => {
    if (map.current) return;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v12', // Satellite-er bodole standard street map diye test korchi
      center: [78.9629, 20.5937],
      zoom: 5
    });
  }, []);

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative', margin: 0, padding: 0 }}>
      <div ref={mapContainer} style={{ width: '100%', height: '100%' }} />
    </div>
  );
}