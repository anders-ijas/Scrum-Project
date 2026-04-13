import "../style/application.css";
export function AppView(props){
    return <div>
        <div>
        <h2>Fråga: {props.question}</h2>
        <h2>Svar: {props.answer}</h2>
        <h2>Säkerhet: {props.accuracy}</h2>
        </div>
        <div class="emotion">
        <h1>Känsla: {props.emotion}</h1>
        </div>
    </div>
    
}