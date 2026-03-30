import { Navigate, Route, Routes } from "react-router-dom";
import Footer from "./components/Footer";
import Header from "./components/Header";
import AboutXAIPage from "./pages/AboutXAIPage";
import DashboardPage from "./pages/DashboardPage";
import EyeCheckPage from "./pages/EyeCheckPage";
import HistoryPage from "./pages/HistoryPage";
import XrayAnalysisPage from "./pages/XrayAnalysisPage";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 max-w-6xl mx-auto px-4 py-6 w-full">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/xray" element={<XrayAnalysisPage />} />
          <Route path="/eye" element={<EyeCheckPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/about" element={<AboutXAIPage />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}
