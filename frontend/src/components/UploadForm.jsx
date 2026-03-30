export default function UploadForm({ patient, setPatient, file, onFileChange, onSubmit, loading }) {
  return (
    <form onSubmit={onSubmit} className="space-y-4 glass-card p-5">
      <div className="grid md:grid-cols-2 gap-3">
        <input className="input" placeholder="Patient Name" value={patient.name} onChange={(e) => setPatient({ ...patient, name: e.target.value })} required />
        <input className="input" placeholder="Age" type="number" value={patient.age} onChange={(e) => setPatient({ ...patient, age: e.target.value })} />
        <input className="input" placeholder="Gender" value={patient.gender} onChange={(e) => setPatient({ ...patient, gender: e.target.value })} />
        <input className="input" placeholder="Doctor" value={patient.doctor} onChange={(e) => setPatient({ ...patient, doctor: e.target.value })} />
      </div>
      <textarea className="input min-h-20" placeholder="Symptoms" value={patient.symptoms} onChange={(e) => setPatient({ ...patient, symptoms: e.target.value })} />
      <input type="file" accept="image/*" onChange={onFileChange} className="block w-full text-sm" required />
      {file && <p className="text-sm text-slate-500">Selected: {file.name}</p>}
      <button disabled={loading} className="bg-medBlue text-white px-4 py-2 rounded-lg disabled:opacity-60 hover-lift">
        {loading ? "Analyzing..." : "Analyze"}
      </button>
    </form>
  );
}
