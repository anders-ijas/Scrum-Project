import {db} from "./firebase_util.js";
import {collection, addDoc, setDoc, doc, query, where, orderBy, getDocs} from "firebase/firestore";import { model } from "./model.js";
import { sessionID } from "./src/index.jsx";

export async function archiveCurrentToPrevious(currentData) {
    if (!currentData || !currentData.question || !currentData.answer) {
        return;
    }
    
    console.log("Archiving:", currentData);
    return addDoc(collection(db, "emotion"), {
        question: currentData.question,
        answer: currentData.answer,
        accuracy: currentData.accuracy,
        emotion: currentData.emotion,
        rawInput: currentData.rawInput,
        dataStream: currentData.dataStream,
        archivedAt: new Date(),
        archived: true,
        sessionID: sessionID
    });
}

export async function saveResult(modelData) {
    return addDoc(collection(db, "emotion"), {
        question: modelData.question,
        answer: modelData.answer,
        accuracy: modelData.accuracy,
        emotion: modelData.emotion,
        rawInput: modelData.rawInput,
        dataStream: modelData.dataStream,
        createdAt: new Date(),
        sessionID: sessionID
    });
}

export async function inita() {
    const data = {
        question: model.question,
        answer: model.answer,
        accuracy: model.accuracy,
        emotion: model.emotion,
        rawInput: model.rawInput,
        dataStream: model.dataStream,
        sessionID: sessionID
    };
    return setDoc(doc(db, "emotion", "current"), data);
}
export async function historyMatch() {
    const q = query(
        collection(db, "emotion"),
        where("sessionID", "==", sessionID),
        orderBy("archivedAt", "asc")
    );
    const snapshot = await getDocs(q);
    return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
}