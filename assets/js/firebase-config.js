import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import { getFirestore, collection, addDoc, onSnapshot, query, orderBy, limit, serverTimestamp, doc, setDoc, increment, getDoc, updateDoc } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";

const firebaseConfig = {
    apiKey: "AIzaSyAqy5XvJKDUxdW7wp5tC2yxE_0hKXrJYvI",
    authDomain: "raffle-draw-app-alph1tech.firebaseapp.com",
    projectId: "raffle-draw-app-alph1tech",
    storageBucket: "raffle-draw-app-alph1tech.appspot.com",
    messagingSenderId: "422199484986",
    appId: "1:422199484986:web:5619a9a670bffe246b0b03",
    measurementId: "G-XCHPLNR2YD",
    databaseURL: "https://raffle-draw-app-alph1tech-default-rtdb.asia-southeast1.firebasedatabase.app"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

export { app, db, collection, addDoc, onSnapshot, query, orderBy, limit, serverTimestamp, doc, setDoc, increment, getDoc, updateDoc };