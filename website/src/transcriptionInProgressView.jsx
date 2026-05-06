export function TranscriptionInProgressView(props) {
    return (
        <div className="app-view">
            <h1>Transkribering pågår...</h1>
            <p>Vänligen vänta medan vi transkriberar och analyserar känslor från din session.</p>
            <div className="loading-spinner"></div>
        </div>
    );
}