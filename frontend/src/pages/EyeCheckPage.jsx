import { useState } from "react";
import CameraCapture from "../components/CameraCapture";
import HeatmapDisplay from "../components/HeatmapDisplay";
import { useApiState } from "../hooks/useApiState";
import { downloadReport, predictEye } from "../services/api";

export default function EyeCheckPage() {
  const [patient, setPatient] = useState({ name: "", age: "", gender: "", symptoms: "", doctor: "" });
  const [captured, setCaptured] = useState("");
  const [result, setResult] = useState(null);
  const [downloading, setDownloading] = useState(false);
  const { loading, error, withLoader } = useApiState();

  const submitEye = async () => {
    if (!captured) return;
    const blob = await (await fetch(captured)).blob();
    const formData = new FormData();
    formData.append("image", blob, "eye_capture.png");
    Object.entries(patient).forEach(([k, v]) => formData.append(k, v));

    await withLoader(async () => {
      const data = await predictEye(formData);
      setResult(data);
    });
  };

  const handleDownload = async () => {
    if (!result?.id) return;
    setDownloading(true);
    try {
      await downloadReport(result.id);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <section className="space-y-4 fade-in">
      <h2 className="text-2xl font-bold text-medBlue">Eye Check (Camera)</h2>
      <p className="text-sm text-slate-600">Position one eye inside the square guide. Only the boxed area is captured and analyzed.</p>
      <div className="grid md:grid-cols-2 gap-4">
        <CameraCapture onCapture={setCaptured} />
        <div className="glass-card p-4 space-y-3">
          <input className="input" placeholder="Patient Name" value={patient.name} onChange={(e) => setPatient({ ...patient, name: e.target.value })} />
          <input className="input" placeholder="Age" type="number" value={patient.age} onChange={(e) => setPatient({ ...patient, age: e.target.value })} />
          <input className="input" placeholder="Gender" value={patient.gender} onChange={(e) => setPatient({ ...patient, gender: e.target.value })} />
          <input className="input" placeholder="Doctor" value={patient.doctor} onChange={(e) => setPatient({ ...patient, doctor: e.target.value })} />
          <textarea className="input min-h-16" placeholder="Symptoms" value={patient.symptoms} onChange={(e) => setPatient({ ...patient, symptoms: e.target.value })} />
          <button onClick={submitEye} disabled={loading || !captured} className="bg-medBlue text-white px-4 py-2 rounded-lg disabled:opacity-60 hover-lift">
            {loading ? "Analyzing..." : "Analyze Eye Image"}
          </button>
        </div>
      </div>
      {loading && <div className="pulse-soft text-medBlue font-medium">Model is analyzing the captured image...</div>}
      {error && <div className="text-red-600">{error}</div>}
      <HeatmapDisplay result={result} />
      {result && (
        <button onClick={handleDownload} disabled={downloading} className="inline-block bg-medBlue text-white px-4 py-2 rounded-lg hover-lift disabled:opacity-60">
          {downloading ? "Downloading PDF..." : "Download PDF Report"}
        </button>
      )}
    </section>
  );
}
