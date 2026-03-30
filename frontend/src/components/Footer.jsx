export default function Footer() {
  return (
    <footer className="mt-12 border-t border-blue-100 py-4 text-center text-sm text-slate-500">
      © {new Date().getFullYear()} MediVision XAI · Explainable AI for healthcare support.
    </footer>
  );
}
