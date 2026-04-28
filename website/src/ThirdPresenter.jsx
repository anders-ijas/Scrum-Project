import { observer } from "mobx-react-lite";
import { useState, useEffect } from "react";
import { historyMatch } from "../persistance.js";
import { HistoryView } from "./historyView.jsx"; // assuming it's exported

export const ThirdPresenter = observer(function ThirdPresenter(props) {
    const [list, setList] = useState([]);

    useEffect(() => {
        async function loadHistory() {
            const docs = await historyMatch();
            // Return objects with question and answer, sorted by archivedAt
            const historyList = docs
                .filter(doc => doc.archived) // only archived docs
                .sort((a, b) => new Date(a.archivedAt) - new Date(b.archivedAt))
                .map(doc => ({
                    question: doc.question,
                    answer: doc.answer
                }));
            setList(historyList);
        }
        loadHistory();
    }, []);

    return <HistoryView
        list={list}
        question={props.model.question}
        answer={props.model.answer}
        accuracy={props.model.accuracy}
        emotion={props.model.emotion}
    />;
});