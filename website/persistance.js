import {db} from "./firebase_util.js";

export function saveResult(model) {
    db.collection("emotion").add({
        question: model.question,
        answer: model.answer,
        accuracy: model.accuracy,
        emotion: model.emotion
    });
}