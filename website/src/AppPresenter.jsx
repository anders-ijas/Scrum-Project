import { observer } from "mobx-react-lite" 
import { AppView } from "./AppView.jsx";
export const AppPresenter = observer(function AppPresenter(props) {
    return <AppView
        question={props.model.question} 
        answer={props.model.answer}
        accuracy={props.model.accuracy}
        emotion={props.model.emotion}
    />
})