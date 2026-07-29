import { startScreenShare, stopScreenShare, joinAsGuest } from './webrtc.js';
import { initChat } from './chat.js';
import { db, doc, setDoc, onSnapshot, serverTimestamp, increment } from './firebase-config.js';
import './stats-sync.js'; // initialize stats sync

window.startScreenShare = startScreenShare;
window.stopScreenShare = stopScreenShare;
window.joinAsGuest = joinAsGuest;

window.increment = increment;
window.db = db;
window.doc = doc;
window.setDoc = setDoc;
window.serverTimestamp = serverTimestamp;



// DOMContentLoaded triggers
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const roomId = urlParams.get('room') || (window.state ? window.state.sessionId : 'default_room');
    const role = urlParams.get('role');
    const isGuest = role === 'guest';
    initChat(roomId, isGuest);
});