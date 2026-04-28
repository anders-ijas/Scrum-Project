import "../style/application.css";

const EMOTIONS = {
  "😐": { label: "Neutral", color: "#666" },
  "😊": { label: "Glad", color: "#4e38a8" },
  "😡": { label: "Rasande", color: "#E24B4A" },
  "😢": { label: "Ledsen", color: "#4A90E2" },
  "😨": { label: "Rädd", color: "#F5A623" },
  "🤢": { label: "Äcklad", color: "#7B8D93" }
};

function SecurityBar({ percentage }) {
  return (
    <div className="security-container">
      <div className="security-header">
        <span>Säkerhet:</span>
        <span className="security-value">{percentage}%</span>
      </div>
      <div className="progress-bg">
        <div className="progress-fill" style={{ width: `${percentage}%` }}></div>
      </div>
    </div>
  );
}

function TipsSection() {
  const tips = [
    "Titta på den vuxnes ansikte när ni pratar",
    "Lyssna noga på vad den vuxne säger",
    "Svara när det känns naturligt",
    "Det är okej att ta pauser och tänka"
  ];

  return (
    <div className="tips-card">
      <h3>
        <span role="img" aria-label="lightbulb">💡</span> Tips under samtalet:
      </h3>
      <ul>
        {tips.map((tip, index) => (
          <li key={index}>{tip}</li>
        ))}
      </ul>
    </div>
  );
}

export function AppView(props) {
  const currentEmotion = EMOTIONS[props.emotion] || { label: "Neutral", color: "#333" };

  return (
    <div className="app-container">
      <div className="emotion-card">
        <div className="emoji-display">
          <div className="emoji-icon">{props.emotion || "😐"}</div>
          <h1 className="emotion-label">{currentEmotion.label}</h1>
        </div>

        <SecurityBar percentage={props.accuracy || 74} />

        <TipsSection />
      </div>
      <div><button className= "Button" onClick={props.onEndAnalysis}> Avsluta Analys</button></div>
    </div>
  );
}