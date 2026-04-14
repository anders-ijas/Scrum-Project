import React, {useEffect} from "react";
import { observer } from "mobx-react-lite" 
import { LandingView } from "./landingView.jsx";

export const LandingPresenter = observer(function LandingPresenter(props) {

    
    return <LandingView/>
})
