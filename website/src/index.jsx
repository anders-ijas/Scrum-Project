import {createElement, Fragment} from "react";
window.React= {createElement:createElement, Fragment:Fragment};
import { reactiveModel } from "../mobXReactiveModel.js";
import { createRoot } from "react-dom/client";
import {Root} from "./root.jsx";
import {fetchData, sessionKeyMaker} from "../util.js";
import { initAnonymousAuth, onAuthReady } from "../firebase_util.js";
import { saveResult, inita, clearAllHistory } from "../persistance.js";
createRoot(document.getElementById('root')).render(<Root model={reactiveModel}/>);
initAnonymousAuth();
export const sessionID = crypto.randomUUID();
onAuthReady(async () => {
    await clearAllHistory();
    inita();
    fetchData();
});