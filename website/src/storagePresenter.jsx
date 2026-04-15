import { observer } from "mobx-react-lite" 
import { StorageView } from "./storageView.jsx";
export const StoragePresenter = observer(function StoragePresenter(props) {
    return <StorageView
        question={props.model.question} 
        answer={props.model.answer}
        accuracy={props.model.accuracy}
        emotion={props.model.emotion}
    />
})