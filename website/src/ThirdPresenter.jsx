import { observer } from "mobx-react-lite";
import { useState, useEffect } from "react";
import { historyMatch } from "../persistance.js";
import { HistoryView } from "./historyView.jsx";
import { parseEmotion } from "../util.js"; // <-- ADDED IMPORT

export const ThirdPresenter = observer(function ThirdPresenter(props) {
    const [list, setList] = useState([]);

    useEffect(() => {
        async function loadHistory() {
            try {
                const docs = await historyMatch();
                const archivedDocs = docs.filter(doc => doc.archived);

                const getTime = (doc) => {
                    if (doc.answerTimestampMs) return Number(doc.answerTimestampMs);
                    if (doc.emotionTimestamp) return Number(doc.emotionTimestamp);
                    return 0;
                };

                const qaEvents = archivedDocs
                    .filter(doc => doc.question && doc.answer)
                    .sort((a, b) => getTime(a) - getTime(b));

                const emotionEvents = archivedDocs
                    .filter(doc => doc.emotion && !doc.question && !doc.answer)
                    .sort((a, b) => getTime(a) - getTime(b));

                const historyList = qaEvents.map((qa, index) => {
                    const currentQaTime = getTime(qa);
                    const previousQaTime = index === 0 ? 0 : getTime(qaEvents[index - 1]);

                    const emotionsInRange = emotionEvents.filter(e => {
                        const eTime = getTime(e);
                        return eTime > previousQaTime && eTime <= currentQaTime;
                    });

                    const rawEmotion = emotionsInRange.length > 0 
                        ? emotionsInRange[emotionsInRange.length - 1].emotion 
                        : (qa.emotion || "😐");

                    return {
                        question: qa.question,
                        answer: qa.answer,
                        // <-- TRANSLATION APPLIED HERE
                        emotion: parseEmotion(rawEmotion) 
                    };
                });

                setList(historyList);
            } catch (error) {
                console.error("Error loading history:", error);
            }
        }
        
        loadHistory();
    }, []);

    return <HistoryView list={list} />;
});