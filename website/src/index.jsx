import {createElement, Fragment} from "react";
window.React= {createElement:createElement, Fragment:Fragment};
import { reactiveModel } from "../mobXReactiveModel.js";
import { createRoot } from "react-dom/client";
import {Root} from "./root.jsx";
import {fetchData} from "../util.js";
createRoot(document.getElementById('root')).render(<Root model={reactiveModel}/>);
fetchData();