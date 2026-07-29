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