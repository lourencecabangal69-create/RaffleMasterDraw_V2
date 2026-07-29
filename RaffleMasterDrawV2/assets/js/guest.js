import { joinAsGuest } from './webrtc.js';
import { initChat } from './chat.js';

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const roomId = urlParams.get('room');
    if (!roomId) {
        alert("Invalid link: Missing room ID");
        return;
    }
    initChat(roomId, true);
    joinAsGuest(roomId).catch(err => {
        console.error("Failed to connect to host:", err);
    });
});