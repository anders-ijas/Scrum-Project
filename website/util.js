import react from "react";
import { reactiveModel } from "./mobXReactiveModel";

export async function fetchData() {
    async function check(){
    const response = await fetch("./mockData.txt");
    const text = await response.text();
    
    parseText(text);
}
    check();
    setInterval(check);
};
export function parseText(text){
    const [question, answer, accuracy, emotion] = text.split(";");
    const parsedEmotion = parseEmotion(emotion);
    reactiveModel.setCurrentQuestion(question);
    reactiveModel.setCurrentAnswer(answer);
    reactiveModel.setCurrentAccuracy(accuracy);
    reactiveModel.setCurrentEmotion(parsedEmotion);
}
export function parseEmotion(emotion){
    switch(emotion){
        case "Glad":
            return "😊";
        case "Ledsen":
            return "😢";
        case "Arg":
            return "😠";
        default:
            return "😐";
    }}