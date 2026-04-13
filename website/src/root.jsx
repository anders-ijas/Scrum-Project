import { observer } from "mobx-react-lite"
import react from "react"
import { AppPresenter } from "./AppPresenter.jsx";

const Root = observer(function root(props){
    return (<div>
        <AppPresenter model={props.model}/>
        </div>)
});
export {Root};