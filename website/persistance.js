import { db } from "./firebase_util.js";
import { collection, addDoc, setDoc, doc, query, where, getDocs, writeBatch } from "firebase/firestore";
import { model } from "./model.js";
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
        emotion: currentData.emotion || "😐",
        rawInput: currentData.rawInput || "",
        dataStream: currentData.dataStream || 0,
        // Using the unified stopwatch timestamps
        emotionTimestamp: currentData.emotionTimestamp || 0, 
        answerTimestampMs: currentData.answerTimestampMs || 0, 
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
        sessionID: sessionID,
        transcribed: false
    };
    return setDoc(doc(db, "emotion", "current"), data);
}

export async function historyMatch() {
    // Removed the orderBy constraint so Firestore returns all documents 
    // for this session, regardless of their exact timestamp field name.
    const q = query(
        collection(db, "emotion"),
        where("sessionID", "==", sessionID)
    );
    const snapshot = await getDocs(q);
    return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
}

export async function clearAllHistory() {
    try {
        const q = collection(db, "emotion");
        const snapshot = await getDocs(q);
        
        const batch = writeBatch(db);
        let deleteCount = 0;
        
        snapshot.docs.forEach((document) => {
            // ONLY delete if the document ID is not "current"
            if (document.id !== "current") {
                batch.delete(doc(db, "emotion", document.id));
                deleteCount++;
            }
        });
        
        // Only commit if there are actually things to delete
        if (deleteCount > 0) {
            await batch.commit();
            console.log(`🗑️ Wiped ${deleteCount} history records. 'current' was kept safe.`);
        } else {
            console.log("No history records found to delete.");
        }
        
    } catch (error) {
        console.error("Error wiping database:", error);
    }
}