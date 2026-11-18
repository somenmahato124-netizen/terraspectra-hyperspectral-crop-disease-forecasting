import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import { MapboxOverlay } from '@deck.gl/mapbox';
import { GeoJsonLayer } from '@deck.gl/layers';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.accessToken =
  import.meta.env.VITE_MAPBOX_TOKEN ||
  import.meta.env.VITE_MAPBOX_ACCESS_TOKEN;

const SAMPLE_FARM_GEOJSON = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: {
        name: 'Sector A - Wheat & Paddy Farm',
        area_acres: 1000,
        crop: 'Wheat & Paddy',
        spectral_bands: 200
      },
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
  const [farmStats, setFarmStats] = useState(null);
  const [hoverInfo, setHoverInfo] = useState(null);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/farm-metadata')
      .then((res) => res.json())
      .then((data) => setFarmStats(data))
      .catch(() => setFarmStats(null));
  }, []);

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
            pickable: true,
            onHover: (info) => setHoverInfo(info.object ? info : null)
          })
        ]
      });

      map.current.addControl(deckOverlay);
    });

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

      {/* Top-Left Live GIS & Pipeline Status Card */}
      <div
        style={{
          position: 'absolute',
          top: 16,
          left: 16,
          backgroundColor: 'rgba(15, 23, 42, 0.88)',
          color: '#f8fafc',
          padding: '14px 18px',
          borderRadius: '10px',
          border: '1px solid rgba(34, 197, 94, 0.45)',
          fontFamily: 'sans-serif',
          zIndex: 10,
          minWidth: '260px'
        }}
      >
        <h2 style={{ margin: 0, fontSize: '18px', color: '#4ade80' }}>TerraSpectra GIS</h2>
        <p style={{ margin: '4px 0 8px', fontSize: '12px', color: '#cbd5e1' }}>
          Sector A • 1,000 Acres • Hyperspectral Base Layer
        </p>
        <div style={{ fontSize: '11px', color: '#94a3b8', borderTop: '1px solid #334155', paddingTop: '8px' }}>
          {farmStats ? (
            <>
              <div>Bands: {farmStats.original_bands} → {farmStats.pca_components} PCA</div>
              <div>Grid: {farmStats.grid_dimensions.height}x{farmStats.grid_dimensions.width} px ({farmStats.crs})</div>
            </>
          ) : (
            <div>Pipeline: 200 Bands → 15 PCA Components</div>
          )}
        </div>
      </div>

      {/* Hover Tooltip */}
      {hoverInfo && (
        <div
          style={{
            position: 'absolute',
            left: hoverInfo.x + 12,
            top: hoverInfo.y + 12,
            backgroundColor: 'rgba(15, 23, 42, 0.92)',
            color: '#f8fafc',
            padding: '8px 12px',
            borderRadius: '6px',
            fontSize: '12px',
            fontFamily: 'sans-serif',
            pointerEvents: 'none',
            border: '1px solid #22c55e',
            zIndex: 20
          }}
        >
          <strong>{hoverInfo.object.properties.name}</strong>
          <div>Area: {hoverInfo.object.properties.area_acres} Acres</div>
          <div>Bands: {hoverInfo.object.properties.spectral_bands} Hyperspectral</div>
        </div>
      )}
    </div>
  );
}