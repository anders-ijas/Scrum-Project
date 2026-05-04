import { observer } from "mobx-react-lite" 
import { AppView } from "./AppView.jsx";
export const AppPresenter = observer(function AppPresenter(props) {
    function setStream() {
    props.model.setDataStream(2);
}
    return <AppView
        question={props.model.question} 
        answer={props.model.answer}
        accuracy={props.model.accuracy}
        emotion={props.model.emotion}
        emotionColor={props.model.emotionColor}
        questionh={props.model.latestSnapshot.question}
        answerh={props.model.latestSnapshot.answer}
        accuracyh={props.model.latestSnapshot.accuracy}
        emotionh={props.model.latestSnapshot.emotion}
        emotionCompare={emotionCompare}
        onEndAnalysis={setStream}
    />
})
function emotionCompare(e1, e2) {
    const levels = {
        "😡": 0, "😠": 1, "😢": 2, "😐": 4, "😊": 5
    };
    return levels[e1] - levels[e2];
}
