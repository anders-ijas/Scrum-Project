import { reactiveModel } from "./mobXReactiveModel.js";
import { db } from "./firebase_util.js";
import { collection, onSnapshot } from "firebase/firestore";

export function fetchData() {
    const emotionsRef = collection(db, "emotion");

    onSnapshot(
        emotionsRef,
        (snapshot) => {
            if (snapshot.empty) return;

            const doc = snapshot.docs[snapshot.docs.length - 1];
            const data = doc.data();
            if (!data) return;

            updateModelFromFirestore(data);
        },
        (error) => {
            console.error("Firestore listener error:", error);
        }
    );
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

    reactiveModel.setCurrentQuestion(question);
    reactiveModel.setCurrentAnswer(answer);
    reactiveModel.setCurrentAccuracy(accuracy);
    reactiveModel.setCurrentEmotion(parsedEmotion);
    reactiveModel.setDataStream(true);
}

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