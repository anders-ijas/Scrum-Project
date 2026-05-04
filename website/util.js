import { reactiveModel } from "./mobXReactiveModel.js";
import { db, initAnonymousAuth } from "./firebase_util.js";
import { doc, onSnapshot } from "firebase/firestore";
import { archiveCurrentToPrevious } from "./persistance.js";

// Track what's currently in Firebase's "current" document
let firebaseCurrentData = {
    question: "",
    answer: "",
    accuracy: "",
    emotion: "",
    rawInput: "",
    dataStream: 0
};

export function fetchData() {
    initAnonymousAuth();
    const docRef = doc(db, "emotion", "current");

    onSnapshot(
        docRef,
        async (docSnap) => {
            if (!docSnap.exists()) {
                console.log("No data in 'emotion/current' yet.");
                return;
            }

            const data = docSnap.data();
            
            // ARCHIVE: Check if question or answer changed BEFORE updating
            if (firebaseCurrentData.question && firebaseCurrentData.answer) {
                if (data.question !== firebaseCurrentData.question || 
                    data.answer !== firebaseCurrentData.answer) {
                    try {
                        await archiveCurrentToPrevious(firebaseCurrentData);
                        console.log("Archived previous data");
                    } catch (error) {
                        console.error("Error archiving data:", error);
                    }
                }
            }
            
            // Update the tracked Firebase data
            firebaseCurrentData = {
                question: String(data.question ?? "").trim(),
                answer: String(data.answer ?? "").trim(),
                accuracy: String(data.accuracy ?? "").trim(),
                emotion: String(data.emotion ?? "").trim(),
                rawInput: data.rawInput ?? "",
                dataStream: data.dataStream ?? 0
            };
            
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
    const question = String(data.question ?? "").trim();
    const answer = String(data.answer ?? "").trim();
    const accuracy = String(data.accuracy ?? "").trim();
    const parsedEmotion = parseEmotion(String(data.emotion || data.emotion || "").trim());
    const emotionColor = parseColorBgr(data.colorBgr);

    if (
        question === reactiveModel.question &&
        answer === reactiveModel.answer &&
        accuracy === reactiveModel.accuracy &&
        parsedEmotion === reactiveModel.emotion &&
        emotionColor === reactiveModel.emotionColor
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
    reactiveModel.setCurrentEmotionColor(emotionColor);
    if (reactiveModel.dataStream != 2) {
        reactiveModel.setDataStream(1);
    }
}
export function historyMatch(){

}

export function parseEmotion(emotion) {
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

function parseColorBgr(colorBgr) {
    if (!Array.isArray(colorBgr) || colorBgr.length < 3) {
        return "";
    }

    const [blue, green, red] = colorBgr.map((value) => Number(value));
    if ([blue, green, red].some((value) => Number.isNaN(value))) {
        return "";
    }

    return `rgb(${red}, ${green}, ${blue})`;
}
export function sessionKeyMaker(){
    const sessionID = crypto.randomUUID();
    return sessionID;
}
