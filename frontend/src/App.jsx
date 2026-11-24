import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import { MapboxOverlay } from '@deck.gl/mapbox';
import { GeoJsonLayer } from '@deck.gl/layers';
import 'mapbox-gl/dist/mapbox-gl.css';
import { createDiseaseHeatmapLayer } from './components/DiseaseHeatmapLayer';

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
  const overlayRef = useRef(null);
  const [farmStats, setFarmStats] = useState(null);
  const [riskGeoJson, setRiskGeoJson] = useState(null);
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [hoverInfo, setHoverInfo] = useState(null);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/farm-metadata')
      .then((res) => res.json())
      .then((data) => setFarmStats(data))
      .catch(() => setFarmStats(null));

    fetch('http://127.0.0.1:8000/api/disease-risk')
      .then((res) => res.json())
      .then((data) => setRiskGeoJson(data))
      .catch(() => setRiskGeoJson(null));
  }, []);

  useEffect(() => {
    if (map.current) return;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/satellite-streets-v12',
      center: [78.9629, 20.5937],
      zoom: 12.5,
      pitch: 50,
      bearing: -15
    });

    map.current.on('load', () => {
      overlayRef.current = new MapboxOverlay({ interleaved: false, layers: [] });
      map.current.addControl(overlayRef.current);
    });

    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!overlayRef.current) return;

    const boundaryLayer = new GeoJsonLayer({
      id: 'farm-boundary-layer',
      data: SAMPLE_FARM_GEOJSON,
      filled: false,
      stroked: true,
      getLineColor: [22, 163, 74, 255],
      getLineWidth: 4,
      lineWidthMinPixels: 2
    });

    const heatmapLayer = createDiseaseHeatmapLayer({
      geojsonData: riskGeoJson,
      visible: showHeatmap,
      onHoverCell: (info) => setHoverInfo(info)
    });

    overlayRef.current.setProps({
      layers: [boundaryLayer, heatmapLayer].filter(Boolean)
    });
  }, [riskGeoJson, showHeatmap]);

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative', overflow: 'hidden' }}>
      <div ref={mapContainer} style={{ width: '100%', height: '100%' }} />

      {/* Top-Left Live GIS & 3D-CNN Status Card */}
      <div
        style={{
          position: 'absolute',
          top: 16,
          left: 16,
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          color: '#f8fafc',
          padding: '14px 18px',
          borderRadius: '10px',
          border: '1px solid rgba(34, 197, 94, 0.45)',
          fontFamily: 'sans-serif',
          zIndex: 10,
          minWidth: '270px'
        }}
      >
        <h2 style={{ margin: 0, fontSize: '18px', color: '#4ade80' }}>TerraSpectra GIS</h2>
        <p style={{ margin: '4px 0 8px', fontSize: '12px', color: '#cbd5e1' }}>
          Sector A • 1,000 Acres • 3D-CNN Disease Forecast
        </p>
        <div style={{ fontSize: '11px', color: '#94a3b8', borderTop: '1px solid #334155', paddingTop: '8px' }}>
          {farmStats ? (
            <>
              <div>Bands: {farmStats.original_bands} → {farmStats.pca_components} PCA</div>
              <div>Grid: {farmStats.grid_dimensions.height}x{farmStats.grid_dimensions.width} px ({farmStats.crs})</div>
            </>
          ) : (
            <div>Pipeline: 200 Bands → 15 PCA → Hybrid 3D-CNN</div>
          )}
        </div>
        <button
          onClick={() => setShowHeatmap((prev) => !prev)}
          style={{
            marginTop: '10px',
            padding: '6px 10px',
            fontSize: '11px',
            backgroundColor: showHeatmap ? '#16a34a' : '#334155',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer'
          }}
        >
          {showHeatmap ? 'Hide 3D Risk Heatmap' : 'Show 3D Risk Heatmap'}
        </button>
      </div>

      {/* Bottom-Left Risk Legend */}
      <div
        style={{
          position: 'absolute',
          bottom: 24,
          left: 16,
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          color: '#f8fafc',
          padding: '10px 14px',
          borderRadius: '8px',
          fontSize: '11px',
          fontFamily: 'sans-serif',
          zIndex: 10
        }}
      >
        <div style={{ fontWeight: 'bold', marginBottom: '6px' }}>Early Crop Stress Risk</div>
        <div>🟢 Healthy (&lt; 35%)</div>
        <div>🟡 Moderate Stress (35% – 64%)</div>
        <div>🔴 High Disease Risk (&ge; 65%)</div>
      </div>

      {/* Cell Hover Tooltip */}
      {hoverInfo && (
        <div
          style={{
            position: 'absolute',
            left: hoverInfo.x + 12,
            top: hoverInfo.y + 12,
            backgroundColor: 'rgba(15, 23, 42, 0.95)',
            color: '#f8fafc',
            padding: '8px 12px',
            borderRadius: '6px',
            fontSize: '12px',
            fontFamily: 'sans-serif',
            pointerEvents: 'none',
            border: '1px solid #ef4444',
            zIndex: 20
          }}
        >
          <strong>{hoverInfo.object.properties.risk_level}</strong>
          <div>Cell ID: {hoverInfo.object.properties.grid_id}</div>
          <div>Stress Prob: {(hoverInfo.object.properties.stress_probability * 100).toFixed(1)}%</div>
        </div>
      )}
    </div>
  );
}