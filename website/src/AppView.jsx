import "../style/application.css";

const EMOTIONS = [
  { level: 0, emoji: "😡", label: "Rasande", labelColor: "#E24B4A" },
  { level: 1, emoji: "😠", label: "Arg", labelColor: "#E07030" },
  { level: 2, emoji: "😢", label: "Ledsen", labelColor: "#c8a000" },
  { level: 3, emoji: "😟", label: "Oroad/Äcklad", labelColor: "#3a8f30" },
  { level: 4, emoji: "😐", label: "Ok, Överraskad", labelColor: "#2077b0" },
  { level: 5, emoji: "😊", label: "Glad", labelColor: "#4e38a8" },
];

const EMOJI_TO_INDEX = { "😡": 0, "😠": 1, "😢": 2,"😨":3,"🤢":3, "😲":4, "😐": 4, "😊": 5 };
const CELL_HEIGHT = 88;
const START_Y = 67; 
const TOTAL_COL_HEIGHT = 660;

function EmotionalThermometer({ emotion, previousEmotion }) {
  const currentIndex = EMOJI_TO_INDEX[emotion] ?? 4;
  const previousIndex = EMOJI_TO_INDEX[previousEmotion] ?? 4;
  
  const currentY = START_Y + (currentIndex * CELL_HEIGHT) + (CELL_HEIGHT / 2);
  const previousY = START_Y + (previousIndex * CELL_HEIGHT) + (CELL_HEIGHT / 2);
  
  const pointsDown = currentY > previousY;
  
  const topBoundary = Math.min(currentY, previousY);
  const bottomBoundary = Math.max(currentY, previousY);

  return (
    <div className="thermo-wrapper">
      <div className="thermo-arrow-col">
        {/* Grå Jämförelsepil */}
        {previousEmotion && emotion !== previousEmotion && (
          <div
            className={`thermo-compare-arrow ${pointsDown ? "thermo-compar e-arrow--down" : "thermo-compare-arrow--up"}`}
            style={{
              top: `${topBoundary}px`,
              bottom: `${TOTAL_COL_HEIGHT - bottomBoundary}px`
            }}
          >
            <div className="thermo-compare-shaft" />
            <div className="thermo-compare-tail" />
            <div className="thermo-compare-head" />
          </div>
        )}

        {/* Svart Huvudpil */}
        <div className="thermo-arrow" style={{ top: `${currentY}px` }}>
          <div className="thermo-arrow-shaft" />
          <div className="thermo-arrow-head" />
          <div className="thermo-arrow-label">{emotion}</div>
        </div>
      </div>

      <div className="thermo-tube">
        <div className="thermo-bulb thermo-bulb--top" />
        <div className="thermo-segments">
          {EMOTIONS.map((e, i) => (
            <div
              key={e.level}
              className="thermo-segment"
              style={{ background: ["#E24B4A", "#F0995B", "#F5CA5B", "#85C97A", "#5BAAD4", "#6B4FCF"][i] }}
            >
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
        <h2>Senaste Fråga: {props.question}</h2>
        <h2>Senaste Svar: {props.answer}</h2>
        <h2>Senaste Säkerhet: {props.accuracy}</h2>
      </div>
      <div className="info-row">
        <h2>Förra Frågan: {props.questionh}</h2>
        <h2>Förra Svaret: {props.answerh}</h2>
        <h2>Förra Säkerheten: {props.accuracyh}</h2>
      </div>
      <div className="emotion">
        <EmotionalThermometer emotion={props.emotion} previousEmotion={props.emotionh} />
      </div>
    </div>
  );
}