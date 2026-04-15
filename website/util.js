import { reactiveModel } from "./mobXReactiveModel.js";
import { db } from "./firebase_util.js";
import { doc, onSnapshot } from "firebase/firestore";

// REMOVED: LOCAL_PREVIOUS_SNAPSHOT_KEY constant

export function fetchData() {
    // REMOVED: loadPreviousSnapshot() call, as we want to start fresh every session

    const docRef = doc(db, "emotion", "current");

    onSnapshot(
        docRef,
        (docSnap) => {
            if (!docSnap.exists()) return;

            const data = docSnap.data();
            updateModelFromFirestore(data);
        },
        (error) => {
            console.error("Firestore listener error:", error);
        }
    );
}

// Rewritten to only move current values to the model's snapshot property in memory
function shiftCurrentToPrevious() {
    const snapshot = {
        question: reactiveModel.question,
        answer: reactiveModel.answer,
        accuracy: reactiveModel.accuracy,
        emotion: reactiveModel.emotion,
        rawInput: reactiveModel.rawInput ?? "",
        timestamp: new Date().toISOString()
    };

    // Only update the model's state; do not touch localStorage
    reactiveModel.setLatestSnapshot(snapshot);
}

function updateModelFromFirestore(data) {
    const question = (data.question ?? "").trim();
    const answer = (data.answer ?? "").trim();
    const accuracy = (data.accuracy ?? "").trim();
    const parsedEmotion = parseEmotion((data.emotion ?? "").trim());

    if (
        question === reactiveModel.question &&
        answer === reactiveModel.answer &&
        accuracy === reactiveModel.accuracy &&
        parsedEmotion === reactiveModel.emotion
    ) {
        return;
    }

    // If dataStream is true, it means we already have "current" data.
    // Move that current data to the "previous" snapshot before updating with new Firestore values.
    if (reactiveModel.dataStream) {
        shiftCurrentToPrevious();
    }

    reactiveModel.setCurrentQuestion(question);
    reactiveModel.setCurrentAnswer(answer);
    reactiveModel.setCurrentAccuracy(accuracy);
    reactiveModel.setCurrentEmotion(parsedEmotion);
    reactiveModel.setDataStream(true);
}

// ... rest of your parseText and parseEmotion functions remain the same
export function parseText(text) {
    const [question, answer, accuracy, emotion] = text.split(";");
    const parsedEmotion = parseEmotion(emotion);
    if (
        question === reactiveModel.question &&
        answer === reactiveModel.answer &&
        accuracy === reactiveModel.accuracy &&
        parsedEmotion === reactiveModel.emotion
    ) {
        return;
    }
    reactiveModel.setCurrentQuestion(question);
    reactiveModel.setCurrentAnswer(answer);
    reactiveModel.setCurrentAccuracy(accuracy);
    reactiveModel.setCurrentEmotion(parsedEmotion);
    reactiveModel.setDataStream(true);
}

export function parseEmotion(emotion) {
    switch (emotion) {
        case "Glad":
            return "😊";
        case "Ledsen":
            return "😢";
        case "Arg":
            return "😠";
        default:
            return "😐";
    }
}