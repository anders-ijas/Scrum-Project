import "../style/application.css";

const EMOTIONS = [
  { level: 0, emoji: "😡", label: "Rasande", desc: "", labelColor: "#E24B4A" },
  { level: 1, emoji: "😠", label: "Arg", desc: "", labelColor: "#E07030" },
  { level: 2, emoji: "😢", label: "Ledsen", desc: "", labelColor: "#c8a000" },
  { level: 3, emoji: "😟", label: "Oroad", desc: "", labelColor: "#3a8f30" },
  { level: 4, emoji: "😐", label: "Ok", desc: "", labelColor: "#2077b0" },
  { level: 5, emoji: "😊", label: "Glad", desc: "", labelColor: "#4e38a8" },
];

const SEGMENT_COLORS = ["#E24B4A", "#F0995B", "#F5CA5B", "#85C97A", "#5BAAD4", "#6B4FCF"];
const EMOJI_TO_INDEX = { "😡": 0, "😠": 1, "😢": 2, "😐": 4, "😊": 5 };
const CELL_HEIGHT = 88;
const BULB_OFFSET = 64;

function EmotionalThermometer({ emotion }) {
  const index = EMOJI_TO_INDEX[emotion] ?? 4;
  const arrowTop = BULB_OFFSET + index * CELL_HEIGHT + CELL_HEIGHT / 2 - 2;

  return (
    <div className="thermo-wrapper">
      <div className="thermo-arrow-col">
        <div className="thermo-arrow" style={{ top: arrowTop }}>
          <div className="thermo-arrow-shaft" />
          <div className="thermo-arrow-head" />
          <div className="thermo-arrow-label">{EMOTIONS[index].emoji}</div>
        </div>
      </div>

      <div className="thermo-tube">
        <div className="thermo-bulb thermo-bulb--top" />
        <div className="thermo-segments">
          {EMOTIONS.map((e, i) => (
            <div key={e.level} className="thermo-segment" style={{ background: SEGMENT_COLORS[i] }}>
              {e.level}
            </div>
          ))}
        </div>
        <div className="thermo-bulb thermo-bulb--bottom" />
      </div>

      <div className="thermo-label-col">
        {EMOTIONS.map((e) => (
          <div key={e.level} className="thermo-cell">
            <div className="thermo-label-name" style={{ color: e.labelColor }}>
              {e.label}
            </div>
            <div className="thermo-label-desc">{e.desc}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function AppView(props) {
  return (
    <div className="app-view">
      <div className="info-row">
        <h2>Fråga: {props.question}</h2>
        <h2>Svar: {props.answer}</h2>
        <h2>Säkerhet: {props.accuracy}</h2>
      </div>
      <div className="emotion">
        <EmotionalThermometer emotion={props.emotion} />
      </div>
    </div>
  );
}