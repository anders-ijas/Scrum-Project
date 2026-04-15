import { set } from "mobx";

export const model = {
    question : "Vad tycker du om min jacka?",
    answer: "den är jättefin!",
    accuracy : "0.9",
    emotion : "Arg",
    rawInput: "",
    dataStream:false,
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
    parseText(text){
        const [question, answer, accuracy, emotion] = text.split(";");
        this.setCurrentQuestion(question);
        this.setCurrentAnswer(answer);
        this.setCurrentAccuracy(accuracy);
        this.setCurrentEmotion(emotion);
    },
    setDataStream(stream){
        this.dataStream = stream;
    }


}