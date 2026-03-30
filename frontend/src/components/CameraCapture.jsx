import { useEffect, useRef, useState } from "react";

export default function CameraCapture({ onCapture }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [captured, setCaptured] = useState("");
  const [cameraError, setCameraError] = useState("");

  const GUIDE_BOX_RATIO = 0.62;

  const getSquareCrop = (width, height) => {
    const size = Math.floor(Math.min(width, height) * GUIDE_BOX_RATIO);
    const x = Math.floor((width - size) / 2);
    const y = Math.floor((height - size) / 2);
    return { x, y, size };
  };

  useEffect(() => {
    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: "user" } })
      .then((stream) => {
        streamRef.current = stream;
        if (videoRef.current) videoRef.current.srcObject = stream;
      })
      .catch(() => setCameraError("Camera access was denied or unavailable."));

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const capture = () => {
    const video = videoRef.current;
    if (!video || !video.videoWidth) return;

    const crop = getSquareCrop(video.videoWidth, video.videoHeight);
    const canvas = document.createElement("canvas");
    canvas.width = crop.size;
    canvas.height = crop.size;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, crop.x, crop.y, crop.size, crop.size, 0, 0, crop.size, crop.size);
    const dataUrl = canvas.toDataURL("image/png");
    setCaptured(dataUrl);
    onCapture(dataUrl);
  };

  const reset = () => {
    setCaptured("");
    onCapture("");
  };

  return (
    <div className="glass-card p-4 space-y-3">
      {cameraError ? (
        <p className="text-sm text-red-600">{cameraError}</p>
      ) : captured ? (
        <div className="space-y-2">
          <img src={captured} alt="captured eye" className="w-full rounded-xl border-2 border-medBlue/20" />
          <p className="text-xs text-slate-500">Only the guided square region was analyzed.</p>
        </div>
      ) : (
        <div className="relative w-full rounded-xl bg-slate-200 overflow-hidden aspect-square md:aspect-[4/3]">
          <video ref={videoRef} autoPlay playsInline className="absolute inset-0 h-full w-full object-cover" />
          <div
            className="absolute border-4 border-medBlue/80 rounded-2xl shadow-[0_0_0_9999px_rgba(2,6,23,0.35)] pointer-events-none"
            style={{
              left: `${((1 - GUIDE_BOX_RATIO) / 2) * 100}%`,
              top: `${((1 - GUIDE_BOX_RATIO) / 2) * 100}%`,
              width: `${GUIDE_BOX_RATIO * 100}%`,
              height: `${GUIDE_BOX_RATIO * 100}%`,
            }}
          />
          <p className="absolute bottom-2 left-1/2 -translate-x-1/2 text-white text-xs bg-slate-900/60 px-2 py-1 rounded-md pointer-events-none">
            Align the eye inside the square
          </p>
        </div>
      )}
      <div className="flex gap-2">
        <button onClick={capture} className="bg-medBlue text-white px-4 py-2 rounded-lg hover-lift">Capture</button>
        {captured && (
          <button onClick={reset} className="bg-slate-200 px-4 py-2 rounded-lg hover-lift">Retake</button>
        )}
      </div>
    </div>
  );
}
