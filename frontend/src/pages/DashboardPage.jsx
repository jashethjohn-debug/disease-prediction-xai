import { Link } from "react-router-dom";

const cards = [
  { title: "X-ray Analysis", icon: "🫁", desc: "Upload chest X-rays and get CNN predictions with Grad-CAM visual explanations.", to: "/xray" },
  { title: "Eye Check", icon: "👁️", desc: "Capture eye images from your camera for rapid AI-assisted screening.", to: "/eye" },
  { title: "History", icon: "🧾", desc: "Review previous analyses, filter records, and download PDF reports.", to: "/history" }
];

export default function DashboardPage() {
  return (
    <section className="space-y-5 fade-in">
      <div className="glass-card p-6">
        <h1 className="text-3xl font-bold text-medBlue">Medical Explainable AI Assistant</h1>
        <p className="mt-2 text-slate-600">Interactive clinical decision-support for chest X-ray and eye-image analysis.</p>
      </div>
      <div className="grid md:grid-cols-3 gap-4">
        {cards.map((card) => (
          <Link key={card.title} to={card.to} className="glass-card hover-lift p-5 group">
            <div className="text-3xl mb-2">{card.icon}</div>
            <h3 className="font-semibold text-medBlue group-hover:underline">{card.title}</h3>
            <p className="mt-2 text-sm text-slate-600">{card.desc}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
