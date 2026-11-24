import { GeoJsonLayer } from '@deck.gl/layers';

export function createDiseaseHeatmapLayer({ geojsonData, visible = true, opacity = 0.72, onHoverCell }) {
  if (!geojsonData || !visible) return null;

  return new GeoJsonLayer({
    id: 'disease-risk-heatmap-layer',
    data: geojsonData,
    filled: true,
    stroked: true,
    extruded: true,
    wireframe: false,
    opacity,
    getElevation: (feature) => {
      const prob = feature.properties?.stress_probability || 0;
      return prob * 140;
    },
    getFillColor: (feature) => {
      const prob = feature.properties?.stress_probability || 0;
      if (prob >= 0.65) return [239, 68, 68, 215];   // Red: High Early Disease Risk
      if (prob >= 0.35) return [250, 204, 21, 195];  // Yellow: Moderate Stress
      return [34, 197, 94, 155];                     // Green: Healthy Crop Canopy
    },
    getLineColor: [15, 23, 42, 95],
    getLineWidth: 1,
    lineWidthMinPixels: 1,
    pickable: true,
    onHover: (info) => {
      if (onHoverCell) {
        onHoverCell(info.object ? info : null);
      }
    },
    updateTriggers: {
      getFillColor: [geojsonData],
      getElevation: [geojsonData]
    }
  });
}