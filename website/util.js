import { reactiveModel } from "./mobXReactiveModel.js";
import { db, initAnonymousAuth } from "./firebase_util.js"; // Added initAnonymousAuth
import { doc, onSnapshot } from "firebase/firestore";

export function fetchData() {
    // 1. Ensure the user is authenticated so the listener has permission
    initAnonymousAuth();

    // 2. IMPORTANT: Collection must match Python script ("emotion_data")
    const docRef = doc(db, "emotion", "current");

    onSnapshot(
        docRef,
        (docSnap) => {
            if (!docSnap.exists()) {
                console.log("No data in 'emotion_data/current' yet.");
                return;
            }

            const data = docSnap.data();
            updateModelFromFirestore(data);
            
        },
        (error) => {
            console.error("Firestore listener error:", error);
        }
    );
}

function shiftCurrentToPrevious() {
    const snapshot = {
        question: reactiveModel.question,
        answer: reactiveModel.answer,
        accuracy: reactiveModel.accuracy,
        emotion: reactiveModel.emotion,
        rawInput: reactiveModel.rawInput ?? "",
        timestamp: new Date().toISOString()
    };
    reactiveModel.setLatestSnapshot(snapshot);
}

function updateModelFromFirestore(data) {
    // FIX: Use String() to prevent .trim() crashes on Numbers (like accuracy)
    const question = String(data.question ?? "").trim();
    const answer = String(data.answer ?? "").trim();
    const accuracy = String(data.accuracy ?? "").trim();
    
    // FIX: Pass the raw emotion to the updated parser
    const parsedEmotion = parseEmotion(String(data.emotion || data.emotion || "").trim());

    if (
        question === reactiveModel.question &&
        answer === reactiveModel.answer &&
        accuracy === reactiveModel.accuracy &&
        parsedEmotion === reactiveModel.emotion
    ) {
        return;
    }

    if (reactiveModel.dataStream) {
        shiftCurrentToPrevious();
    }

    reactiveModel.setCurrentQuestion(question);
    reactiveModel.setCurrentAnswer(answer);
    reactiveModel.setCurrentAccuracy(accuracy);
    reactiveModel.setCurrentEmotion(parsedEmotion);
    reactiveModel.setDataStream(true);
}

export function parseEmotion(emotion) {
    // FIX: Model sends English (e.g., "happiness"), website uses Swedish logic
    switch (emotion.toLowerCase()) {
        case "happiness":
        case "glad":
            return "😊";
        case "sadness":
        case "ledsen":
            return "😢";
        case "anger":
        case "arg":
            return "😠";
        case "fear":
        case "rädd":
            return "😨";
        case "disgust":
        case "äcklad":
            return "🤢";
        case "surprise":
        case "förvånad":
            return "😲";
        default:
            return "😐";
    }
}