import { useEffect, useMemo, useState } from "react";
import HistoryTable from "../components/HistoryTable";
import { fetchHistory } from "../services/api";

export default function HistoryPage() {
  const [records, setRecords] = useState([]);
  const [query, setQuery] = useState("");
  const [type, setType] = useState("all");

  useEffect(() => {
    fetchHistory().then(setRecords).catch(() => setRecords([]));
  }, []);

  const filtered = useMemo(() => {
    return records.filter((r) => {
      const q = query.toLowerCase();
      const queryMatch = !q || r.name.toLowerCase().includes(q) || r.disease.toLowerCase().includes(q);
      const typeMatch = type === "all" || r.test_type === type;
      return queryMatch && typeMatch;
    });
  }, [records, query, type]);

  return (
    <section className="space-y-4 fade-in">
      <h2 className="text-2xl font-bold text-medBlue">History</h2>
      <div className="glass-card p-4 grid md:grid-cols-3 gap-3 items-center">
        <input className="input md:col-span-2" placeholder="Filter by patient or disease" value={query} onChange={(e) => setQuery(e.target.value)} />
        <select className="input" value={type} onChange={(e) => setType(e.target.value)}>
          <option value="all">All test types</option>
          <option value="xray">X-ray</option>
          <option value="eye">Eye</option>
        </select>
        <p className="text-sm text-slate-600 md:col-span-3">Showing <span className="font-semibold text-medBlue">{filtered.length}</span> of {records.length} records.</p>
      </div>
      <HistoryTable records={filtered} />
    </section>
  );
}
