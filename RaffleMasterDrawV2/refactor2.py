import os
import re

def main():
    base_dir = r"c:\Users\loure\Downloads\web-development\RaffleMasterDraw-main\RaffleMasterDraw-main"
    
    # Read index.html
    index_path = os.path.join(base_dir, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        index_content = f.read()

    # We will extract the module script logic (excluding imports and PeerJS/WebRTC)
    scripts = re.findall(r'<script.*?>(.*?)</script>', index_content, re.DOTALL)
    
    module_script = scripts[0] if len(scripts) > 0 else ""
    iife_script = scripts[1] if len(scripts) > 1 else ""
    
    # Clean the module script (remove imports, firebase config, and old WebRTC)
    # We will extract only the global stats and session state sync logic.
    stats_sync_logic = """
import { db, doc, onSnapshot, setDoc, serverTimestamp } from './firebase-config.js';

const statsDoc = doc(db, "stats", "global");
const visitsDoc = doc(db, "visits", "global");

// Global Stats Live Listener
onSnapshot(statsDoc, (snap) => {
    if (snap.exists()) {
        const data = snap.data();
        const drawnEl = document.getElementById('logDrawnCount');
        const elimEl = document.getElementById('logEliminatedCount');
        if (drawnEl) drawnEl.textContent = data.drawn || 0;
        if (elimEl) elimEl.textContent = data.eliminated || 0;
    }
});

// Visits Live Listener
let globalVisitCount = 0;
onSnapshot(visitsDoc, (snap) => {
    if (snap.exists()) {
        const data = snap.data();
        globalVisitCount = data.totalVisits || 0;
        const globalVisitEl = document.getElementById('logGlobalVisitCount');
        if (globalVisitEl) globalVisitEl.textContent = globalVisitCount;
    }
});

// Session State Sync
let sessionUnsubscribe = null;
window.syncSessionState = async () => {
    if (!state.sessionId || state.isGuest) return;
    try {
        await setDoc(doc(db, "raffle_sessions", state.sessionId), {
            entrants: state.entrants || [],
            eliminatedIds: state.eliminatedIds || [],
            topWinners: state.topWinners || [],
            consolationWinners: state.consolationWinners || [],
            prizes: state.prizes || { top: {}, consolation: {} },
            topSlots: state.topSlots || 3,
            consolationEnabled: state.consolationEnabled || false,
            consolationLimit: state.consolationLimit || 3,
            theme: state.theme || 'wheel',
            isDrawing: state.isDrawing || false,
            eliminationModeActive: state.eliminationModeActive !== undefined ? state.eliminationModeActive : true,
            wheelRotation: state.wheelRotation || 0,
            lastUpdated: serverTimestamp()
        }, { merge: true });
    } catch (err) {
        console.error("Failed to sync session state:", err);
    }
};

window.listenToSessionState = function(sessionId) {
    if (sessionUnsubscribe) {
        sessionUnsubscribe();
        sessionUnsubscribe = null;
    }
    
    const sessionRef = doc(db, "raffle_sessions", sessionId);
    sessionUnsubscribe = onSnapshot(sessionRef, (snap) => {
        if (snap.exists() && state.isGuest) {
            const data = snap.data();
            state.entrants = data.entrants || [];
            state.eliminatedIds = data.eliminatedIds || [];
            state.topWinners = data.topWinners || [];
            state.consolationWinners = data.consolationWinners || [];
            state.prizes = data.prizes || { top: {}, consolation: {} };
            state.topSlots = data.topSlots || 3;
            state.consolationEnabled = data.consolationEnabled || false;
            state.consolationLimit = data.consolationLimit || 3;
            state.theme = data.theme || 'wheel';
            state.eliminationModeActive = data.eliminationModeActive !== undefined ? data.eliminationModeActive : true;
            state.wheelRotation = data.wheelRotation || 0;
            state.isDrawing = data.isDrawing || false;
            
            if (typeof renderAll === 'function') renderAll();
        }
    });
};
"""

    with open(os.path.join(base_dir, "assets", "js", "stats-sync.js"), "w", encoding="utf-8") as f:
        f.write(stats_sync_logic.strip())

    # We need to prepend the imports to main_logic and ensure `stats-sync.js` is imported.
    # main_logic is currently the IIFE. We should just append the IIFE.
    
    new_main_js = f"""
import {{ startScreenShare, stopScreenShare, joinAsGuest }} from './webrtc.js';
import {{ initChat }} from './chat.js';
import {{ db, doc, setDoc, onSnapshot, serverTimestamp, increment }} from './firebase-config.js';
import './stats-sync.js'; // initialize stats sync

window.startScreenShare = startScreenShare;
window.stopScreenShare = stopScreenShare;
window.joinAsGuest = joinAsGuest;

window.increment = increment;
window.db = db;
window.doc = doc;
window.setDoc = setDoc;
window.serverTimestamp = serverTimestamp;

{iife_script}

// DOMContentLoaded triggers
document.addEventListener('DOMContentLoaded', () => {{
    const urlParams = new URLSearchParams(window.location.search);
    const roomId = urlParams.get('room') || (window.state ? window.state.sessionId : 'default_room');
    const role = urlParams.get('role');
    const isGuest = role === 'guest';
    initChat(roomId, isGuest);
}});
"""
    with open(os.path.join(base_dir, "assets", "js", "main.js"), "w", encoding="utf-8") as f:
        f.write(new_main_js.strip())

if __name__ == "__main__":
    main()
