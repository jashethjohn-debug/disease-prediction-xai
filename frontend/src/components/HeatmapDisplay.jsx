import { useState } from "react";
import { fileUrl } from "../services/api";

export default function HeatmapDisplay({ result }) {
  const [showHeatmap, setShowHeatmap] = useState(true);
  if (!result) return null;

  const confidencePercent = (result.confidence * 100).toFixed(2);
  const riskColor = result.risk_level === "High" ? "bg-red-500" : result.risk_level === "Moderate" ? "bg-amber-500" : "bg-emerald-500";

  return (
    <section className="glass-card p-5 space-y-4 fade-in">
      <div>
        <h3 className="text-xl font-semibold text-medBlue">Prediction: {result.disease}</h3>
        <p className="text-slate-600">Confidence: {confidencePercent}%</p>
        <div className="w-full h-3 bg-blue-100 rounded-full mt-2 overflow-hidden">
          <div className="h-full bg-medBlue transition-all duration-700" style={{ width: `${confidencePercent}%` }} />
        </div>
        <span className={`inline-block mt-2 text-white px-2 py-1 text-xs rounded ${riskColor}`}>Risk: {result.risk_level}</span>
      </div>

      <div className="flex gap-2">
        <button onClick={() => setShowHeatmap(false)} className={`px-3 py-1 rounded-full text-sm ${!showHeatmap ? "bg-medBlue text-white" : "bg-blue-50 text-medBlue"}`}>Original</button>
        <button onClick={() => setShowHeatmap(true)} className={`px-3 py-1 rounded-full text-sm ${showHeatmap ? "bg-medBlue text-white" : "bg-blue-50 text-medBlue"}`}>Grad-CAM</button>
      </div>

      <img
        src={showHeatmap ? fileUrl(result.heatmap_url) : fileUrl(result.image_url)}
        alt={showHeatmap ? "heatmap" : "original"}
        className="rounded-xl max-h-[420px] object-contain w-full bg-white"
      />
    </section>
  );
}
