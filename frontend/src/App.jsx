import React, { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import { MapboxOverlay } from '@deck.gl/mapbox';
import { GeoJsonLayer } from '@deck.gl/layers';
import 'mapbox-gl/dist/mapbox-gl.css';

// .env file theke Mapbox token load kora hocche
mapboxgl.accessToken =
  import.meta.env.VITE_MAPBOX_TOKEN ||
  import.meta.env.VITE_MAPBOX_ACCESS_TOKEN;

// Sample 1,000-acre farm boundary (GeoJSON format)
const SAMPLE_FARM_GEOJSON = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: { name: 'Sector A - Wheat & Paddy Farm', area_acres: 1000 },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [78.9500, 20.5800],
            [78.9750, 20.5800],
            [78.9750, 20.6050],
            [78.9500, 20.6050],
            [78.9500, 20.5800]
          ]
        ]
      }
    }
  ]
};

export default function App() {
  const mapContainer = useRef(null);
  const map = useRef(null);

  useEffect(() => {
    if (map.current) return;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/satellite-streets-v12',
      center: [78.9629, 20.5937],
      zoom: 12,
      pitch: 45,
      bearing: 0
    });

    // Map load howar por Deck.gl overlay add kora
    map.current.on('load', () => {
      const deckOverlay = new MapboxOverlay({
        interleaved: false,
        layers: [
          new GeoJsonLayer({
            id: 'farm-boundary-layer',
            data: SAMPLE_FARM_GEOJSON,
            filled: true,
            stroked: true,
            getFillColor: [34, 197, 94, 100],
            getLineColor: [22, 163, 74, 255],
            getLineWidth: 5,
            lineWidthMinPixels: 2,
            pickable: true
          })
        ]
      });

      map.current.addControl(deckOverlay);
    });

    // Navigation zoom/tilt controls
    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative', overflow: 'hidden' }}>
      <div ref={mapContainer} style={{ width: '100%', height: '100%' }} />

      {/* Top-Left Dashboard Header Overlay */}
      <div
        style={{
          position: 'absolute',
          top: 16,
          left: 16,
          backgroundColor: 'rgba(15, 23, 42, 0.85)',
          color: '#f8fafc',
          padding: '12px 18px',
          borderRadius: '8px',
          border: '1px solid rgba(34, 197, 94, 0.4)',
          fontFamily: 'sans-serif',
          zIndex: 10
        }}
      >
        <h2 style={{ margin: 0, fontSize: '18px', color: '#4ade80' }}>TerraSpectra GIS</h2>
        <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#cbd5e1' }}>
          Sector A • 1,000 Acres • Hyperspectral Base Layer
        </p>
      </div>
    </div>
  );
}