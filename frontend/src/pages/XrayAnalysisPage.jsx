import { useState } from "react";
import HeatmapDisplay from "../components/HeatmapDisplay";
import UploadForm from "../components/UploadForm";
import { useApiState } from "../hooks/useApiState";
import { downloadReport, predictXray } from "../services/api";

export default function XrayAnalysisPage() {
  const [patient, setPatient] = useState({ name: "", age: "", gender: "", symptoms: "", doctor: "" });
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState(null);
  const [downloading, setDownloading] = useState(false);
  const { loading, error, withLoader } = useApiState();

  const onFileChange = (e) => {
    const selected = e.target.files?.[0];
    if (!selected) return;
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("image", file);
    Object.entries(patient).forEach(([k, v]) => formData.append(k, v));

    await withLoader(async () => {
      const data = await predictXray(formData);
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
      <h2 className="text-2xl font-bold text-medBlue">X-ray Analysis</h2>
      <UploadForm patient={patient} setPatient={setPatient} file={file} onFileChange={onFileChange} onSubmit={onSubmit} loading={loading} />
      {preview && <img src={preview} alt="preview" className="max-w-sm rounded-xl shadow" />}
      {loading && <div className="pulse-soft text-medBlue font-medium">Processing image and generating Grad-CAM...</div>}
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
