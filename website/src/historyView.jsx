import "../style/history.css";
export function HistoryView(props) {
  return (
    <div className="history-view">
      <h2>Historik</h2>
      <p>Här kan du se tidigare samtal och hur känslorna har förändrats över tid.</p>
      <div className="history-list">
        {props.list.map((entry, index) => (
          <div key={index} className="history-entry">
            <div className="entry-step adult">
              <div className="avatar adult">
                {/* adult icon svg */}
              </div>
              <div className="step-content">
                <span className="step-label adult">STEG 1: VUXEN SÄGER</span>
                <p className="step-text">"{entry.question}"</p>
              </div>
            </div>

            <div className="entry-step child">
              <div className="avatar child">😊</div>
              <div className="step-content">
                <span className="step-label child">STEG 2: DU SVARAR</span>
                <p className="step-text">"{entry.answer}"</p>
              </div>
            </div>

            <div className="emotion-row">
              <span className="emotion-label">Känsla:</span>
              <span className="emotion-badge">{entry.emotion}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}