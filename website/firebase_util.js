import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getAuth, signInAnonymously, onAuthStateChanged } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyAVrc0MdIJlcKXDdwBy101WNbTz5W4lzsc",
  authDomain: "emotion-tester-2efe7.firebaseapp.com",
  projectId: "emotion-tester-2efe7",
  storageBucket: "emotion-tester-2efe7.firebasestorage.app",
  messagingSenderId: "896791685311",
  appId: "1:896791685311:web:e4253697821ee80c013e0a"
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
export const auth = getAuth(app);

export function initAnonymousAuth() {
  signInAnonymously(auth).catch((error) => {
    console.error("Anonymous auth failed:", error);
  });
}

export function onAuthReady(callback) {
  return onAuthStateChanged(auth, (user) => {
    if (user) {
      callback(user);
    }
  });
}