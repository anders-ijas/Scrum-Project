import { observer } from "mobx-react-lite";
import {TranscriptionInProgressView} from "./transcriptionInProgressView.jsx";

export const TranscriptionInProgressPresenter = observer(function TranscriptionInProgressPresenter(props) {
    return <TranscriptionInProgressView/>
})