import { set } from "mobx";

export const model = {
    question : "",
    answer: "",
    accuracy : "",
    emotion : "😐",
    emotionColor: "",
    rawInput: "",
    dataStream:0,
    transcribed: false,
    latestSnapshot: {
        question : "",
        answer: "",
        accuracy : "",
        emotion : "",
        rawInput: "",
        timestamp: null
    },
    setCurrentQuestion (question){
        this.question = question;
    },
    setCurrentAnswer(answer){
        this.answer = answer;
    },
    setCurrentAccuracy(accuracy){
        this.accuracy = accuracy;
    },
    setCurrentEmotion(emotion){
        this.emotion = emotion;
    },
    setCurrentEmotionColor(color){
        this.emotionColor = color;
    },
    setLatestSnapshot(snapshot) {
        this.latestSnapshot = snapshot;
    },
    parseText(text){
        const [question, answer, accuracy, emotion] = text.split(";");
        this.setCurrentQuestion(question);
        this.setCurrentAnswer(answer);
        this.setCurrentAccuracy(accuracy);
        this.setCurrentEmotion(emotion);
    },
    setDataStream(stream){
        this.dataStream = stream;
    },
    setTranscribed(transcribed) {
        this.transcribed = transcribed;
    }
}
