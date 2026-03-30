export default function AboutXAIPage() {
  return (
    <section className="bg-white/70 rounded-2xl shadow-glass p-6 space-y-4">
      <h2 className="text-2xl font-bold text-medBlue">About Explainable AI (XAI)</h2>
      <p>
        A Convolutional Neural Network (CNN) learns image patterns (edges, textures, lesions) through layers. In this app,
        CNNs estimate the likely disease class from X-ray and eye images.
      </p>
      <p>
        Grad-CAM is an explainability method that highlights image regions most responsible for the model decision.
        Brighter areas on the heatmap indicate stronger influence on prediction.
      </p>
      <p className="text-slate-600 text-sm">
        This tool is decision support only and should not replace professional diagnosis.
      </p>
    </section>
  );
}
