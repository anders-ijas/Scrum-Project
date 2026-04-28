import { observable, configure } from "mobx";
import {model} from "./model.js";

configure({ enforceActions: "never", });  
export const reactiveModel = observable(model);