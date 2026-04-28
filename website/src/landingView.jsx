import "../style/landing.css";

export function LandingView(props) {
  return (
    <div className="landing-container">
      <div className="landing-card">
        {/* Connection Icon */}
        <div className="connection-icon-wrapper">
          <div className="wifi-icon">
            <span role="img" aria-label="wifi">📶</span>
          </div>
        </div>

        {/* Status Text */}
        <h1 className="status-title">Ansluter till systemet...</h1>
        <p className="status-subtitle">
          Väntar på kontakt med Raspberry Pi och analysdator
        </p>

        {/* Animated Loading Dots */}
        <div className="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>

        {/* Information Box */}
        <div className="info-box">
          <h3 className="info-title">Vad händer nu?</h3>
          <ul className="info-list">
            <li>
              <span className="info-bullet"></span>
              Systemet kontaktar Raspberry Pi
            </li>
            <li>
              <span className="info-bullet"></span>
              Kontrollerar att kamera och mikrofon fungerar
            </li>
            <li>
              <span className="info-bullet"></span>
              Laddar AI-modeller för känslor och tal
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
