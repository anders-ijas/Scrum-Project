import "../style/application.css";
export function StorageView(props) {
    return (
        <div className="app-view">
            <div className="info-row">
                <h2>Fråga: {props.question}</h2>
                <h2>Svar: {props.answer}</h2>
                <h2>Säkerhet: {props.accuracy}</h2>
                <h1>Känsla:{props.emotion}</h1>
                <button>Detaljer</button>

            </div>
            <div className="emotion">
            </div>
        </div>
    );
}