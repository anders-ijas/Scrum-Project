import { observer } from "mobx-react-lite"
import react from "react"
import { AppPresenter } from "./AppPresenter.jsx";
import { LandingPresenter } from "./landingPresenter.jsx";
import { ThirdPresenter } from "./ThirdPresenter.jsx";
import { TranscriptionInProgressPresenter } from "./TranscriptionInProgressPresenter.jsx";
const Root = observer(function root(props) {
  return (
    <div>
      {props.model.dataStream === 1 ? (
        <AppPresenter model={props.model} />
      ) : props.model.dataStream === 2 && props.model.transcribed ? (
        <ThirdPresenter model={props.model} />
      ): props.model.dataStream === 2 && !props.model.transcribed ? (
        <TranscriptionInProgressPresenter model={props.model} />
      )
       :
       (
        <LandingPresenter model={props.model} />
      )}
    </div>
  );
});
export {Root};