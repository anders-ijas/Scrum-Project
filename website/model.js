export const model = {
    question : "",
    answer: "",
    accuracy : null,
    emotion : "",
    rawInput: "",
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
    }


}