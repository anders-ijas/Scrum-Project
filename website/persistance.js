import {db} from "./firebase_util.js";
import {collection, addDoc, setDoc, doc} from "firebase/firestore";
import { model } from "./model.js";

export async function saveResult(modelData) {
    return addDoc(collection(db, "emotion"), {
        question: modelData.question,
        answer: modelData.answer,
        accuracy: modelData.accuracy,
        emotion: modelData.emotion,
        rawInput: modelData.rawInput,
        dataStream: modelData.dataStream,
        createdAt: new Date()
    });}

export async function inita() {
    const data = {
        question: model.question,
        answer: model.answer,
        accuracy: model.accuracy,
        emotion: model.emotion,
        rawInput: model.rawInput,
        dataStream: model.dataStream
    };
    return setDoc(doc(db, "emotion", "current"), data);
}