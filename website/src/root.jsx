import { observer } from "mobx-react-lite"
import react from "react"
import { AppPresenter } from "./AppPresenter.jsx";
import { LandingPresenter } from "./landingPresenter.jsx";

const Root = observer(function root(props){
    return (<div>
        {props.model.dataStream ?(
        <AppPresenter model={props.model}/>) : (<LandingPresenter model={props.model}/>)}
        </div>)
});
export {Root};