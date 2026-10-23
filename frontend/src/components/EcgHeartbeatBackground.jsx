export default function EcgHeartbeatBackground() {
  return <div className="ecg-background" aria-hidden="true">
    <svg viewBox="0 0 1200 300" preserveAspectRatio="none">
      <defs><linearGradient id="ecg-fade" x1="0" x2="1"><stop offset="0" stopColor="#0b3c65" stopOpacity="0"/><stop offset=".18" stopColor="#0b3c65" stopOpacity=".5"/><stop offset=".82" stopColor="#0b3c65" stopOpacity=".5"/><stop offset="1" stopColor="#0b3c65" stopOpacity="0"/><animate attributeName="x1" values="0;-.2;0" dur="4s" repeatCount="indefinite"/></linearGradient><radialGradient id="ecg-halo"><stop stopColor="#fb6376" stopOpacity=".28"/><stop offset="1" stopColor="#fb6376" stopOpacity="0"/></radialGradient></defs>
      <path className="ecg-trace" d="M0 158 H130 Q150 158 164 142 Q180 128 194 158 H268 L290 174 L315 66 L340 216 L361 142 L382 158 H520 Q540 158 554 142 Q570 128 584 158 H658 L680 174 L705 66 L730 216 L751 142 L772 158 H910 Q930 158 944 142 Q960 128 974 158 H1200" pathLength="1000" />
      <circle className="ecg-halo" r="50" fill="url(#ecg-halo)"/><circle className="ecg-marker" r="4" />
    </svg>
  </div>;
}
