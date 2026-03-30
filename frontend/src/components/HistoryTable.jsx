import { useState } from "react";
import { Link } from "react-router-dom";
import { downloadReport } from "../services/api";

export default function HistoryTable({ records }) {
  const [activeDownloadId, setActiveDownloadId] = useState(null);

  const handleDownload = async (id) => {
    setActiveDownloadId(id);
    try {
      await downloadReport(id);
    } finally {
      setActiveDownloadId(null);
    }
  };

  return (
    <div className="overflow-x-auto bg-white/70 rounded-2xl p-4 shadow-glass">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="text-left text-medBlue border-b">
            <th className="p-2">Patient</th><th className="p-2">Test</th><th className="p-2">Disease</th><th className="p-2">Confidence</th><th className="p-2">Date</th><th className="p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {records.map((r) => (
            <tr key={r.id} className="border-b border-blue-50">
              <td className="p-2">{r.name}</td>
              <td className="p-2">{r.test_type}</td>
              <td className="p-2">{r.disease}</td>
              <td className="p-2">{(r.confidence * 100).toFixed(1)}%</td>
              <td className="p-2">{r.date}</td>
              <td className="p-2 flex gap-2">
                <button onClick={() => handleDownload(r.id)} disabled={activeDownloadId === r.id} className="text-medBlue underline disabled:opacity-50">
                  {activeDownloadId === r.id ? "Downloading..." : "PDF"}
                </button>
                <Link to={r.test_type === "xray" ? "/xray" : "/eye"} className="text-slate-600 underline">Retest</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
