export function HistoryView(props) {
    return (
        <div className="history-view">
            <h2>Historik</h2>
            <p>Här kan du se tidigare samtal och hur känslorna har förändrats över tid.</p>
            <div className="history-list">
                {props.list.map((entry, index) => (
                    <div key={index} className="history-entry">
                        <h3>Fråga: {entry.question}</h3>
                        <p>Svar: {entry.answer}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}