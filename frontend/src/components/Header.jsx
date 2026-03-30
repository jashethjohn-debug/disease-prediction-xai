import { Link, NavLink } from "react-router-dom";

const links = [
  ["/", "Dashboard"],
  ["/xray", "X-ray Analysis"],
  ["/eye", "Eye Check"],
  ["/history", "History"],
  ["/about", "About XAI"]
];

export default function Header() {
  return (
    <header className="sticky top-0 z-20 backdrop-blur bg-white/75 border-b border-blue-100">
      <div className="max-w-6xl mx-auto px-4 py-3 flex flex-wrap gap-3 items-center justify-between">
        <Link to="/" className="font-bold text-medBlue text-xl">MediVision XAI</Link>
        <nav className="flex flex-wrap gap-2">
          {links.map(([to, label]) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-full text-sm ${isActive ? "bg-medBlue text-white" : "bg-blue-50 text-medBlue"}`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
}
