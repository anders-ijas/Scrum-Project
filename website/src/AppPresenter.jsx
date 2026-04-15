import { observer } from "mobx-react-lite" 
import { AppView } from "./AppView.jsx";
export const AppPresenter = observer(function AppPresenter(props) {
    return <AppView
        question={props.model.question} 
        answer={props.model.answer}
        accuracy={props.model.accuracy}
        emotion={props.model.emotion}
        questionh={props.model.latestSnapshot.question}
        answerh={props.model.latestSnapshot.answer}
        accuracyh={props.model.latestSnapshot.accuracy}
        emotionh={props.model.latestSnapshot.emotion}
        emotionCompare={emotionCompare}
    />
})
function emotionCompare(e1, e2) {
    const levels = {
        "😡": 0, "😠": 1, "😢": 2, "😐": 4, "😊": 5
    };
    return levels[e1] - levels[e2];
}