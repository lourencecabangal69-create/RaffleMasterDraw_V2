import os
import re

def main():
    base_dir = r"c:\Users\loure\Downloads\web-development\RaffleMasterDraw-main\RaffleMasterDraw-main"
    
    # Create directories
    os.makedirs(os.path.join(base_dir, "assets", "css"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "assets", "js"), exist_ok=True)
    
    # Read index.html
    index_path = os.path.join(base_dir, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        index_content = f.read()

    # Read guest.html
    guest_path = os.path.join(base_dir, "guest.html")
    with open(guest_path, "r", encoding="utf-8") as f:
        guest_content = f.read()

    # Extract all styles from index.html
    style_matches = re.finditer(r'<style>(.*?)</style>', index_content, re.DOTALL)
    combined_css = ""
    for match in style_matches:
        combined_css += match.group(1).strip() + "\n\n"
    
    with open(os.path.join(base_dir, "assets", "css", "style.css"), "w", encoding="utf-8") as f:
        f.write(combined_css)
        
    # Extract styles from guest.html
    guest_style_matches = re.finditer(r'<style>(.*?)</style>', guest_content, re.DOTALL)
    guest_css = ""
    for match in guest_style_matches:
        guest_css += match.group(1).strip() + "\n\n"
        
    with open(os.path.join(base_dir, "assets", "css", "guest.css"), "w", encoding="utf-8") as f:
        f.write(guest_css)
        
    # Remove styles from index.html and insert link
    index_content = re.sub(r'<style>.*?</style>', '', index_content, flags=re.DOTALL)
    index_content = index_content.replace('</head>', '<link rel="stylesheet" href="assets/css/style.css">\n</head>')
    
    # Remove styles from guest.html and insert link
    guest_content = re.sub(r'<style>.*?</style>', '', guest_content, flags=re.DOTALL)
    guest_content = guest_content.replace('</head>', '<link rel="stylesheet" href="assets/css/guest.css">\n</head>')
    
    # --- JAVASCRIPT REFACTORING ---
    
    firebase_config = """
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
"""
    with open(os.path.join(base_dir, "assets", "js", "firebase-config.js"), "w", encoding="utf-8") as f:
        f.write(firebase_config.strip())

    webrtc_js = """
import { db, doc, setDoc, serverTimestamp, onSnapshot } from './firebase-config.js';

let Peer = window.Peer;

export async function initPeer() {
    if (!Peer) {
        await new Promise(resolve => {
            const check = setInterval(() => {
                if (window.Peer) { Peer = window.Peer; clearInterval(check); resolve(); }
            }, 100);
        });
    }
}

export async function startScreenShare(roomId) {
    await initPeer();
    try {
        const stream = await navigator.mediaDevices.getDisplayMedia({
            video: { displaySurface: "browser", cursor: "always" },
            audio: false
        });
        
        window.hostStream = stream;
        const hostPeer = new Peer('raffle-host-' + roomId, { debug: 2 });
        
        hostPeer.on('open', (id) => {
            console.log('Host Peer open with ID:', id);
            if (window.showToast) window.showToast('📺 Screen sharing started! Share the guest link.', 'success');
        });
        
        hostPeer.on('call', (call) => {
            console.log('Guest is calling. Answering with screen stream...');
            call.answer(stream);
        });
        
        stream.getVideoTracks()[0].onended = function() {
            stopScreenShare(roomId);
        };
        
        window.hostPeer = hostPeer;
        return hostPeer;
    } catch (err) {
        console.error('Screen share error:', err);
        if (window.showToast) window.showToast('❌ Failed to start screen sharing: ' + err.message, 'error');
        throw err;
    }
}

export async function stopScreenShare(roomId) {
    if (window.hostStream) {
        window.hostStream.getTracks().forEach(t => t.stop());
    }
    if (window.hostPeer) {
        window.hostPeer.destroy();
    }
    if (window.showToast) window.showToast('📺 Screen sharing stopped', 'info');
}

export async function joinAsGuest(roomId) {
    await initPeer();
    return new Promise((resolve, reject) => {
        const guestPeer = new Peer({ debug: 2 });
        guestPeer.on('open', (id) => {
            console.log('Guest peer opened. Calling host: raffle-host-' + roomId);
            const call = guestPeer.call('raffle-host-' + roomId, window.localStream || null);
            
            call.on('stream', (remoteStream) => {
                const videoEl = document.getElementById('guestVideo');
                if (videoEl) {
                    videoEl.srcObject = remoteStream;
                    videoEl.play();
                }
                const liveIndicator = document.getElementById('liveIndicator');
                const connectionStatus = document.getElementById('connectionStatus');
                const statusDot = document.getElementById('statusDot');
                const statusText = document.getElementById('statusText');
                
                if (liveIndicator) liveIndicator.classList.remove('hidden');
                if (connectionStatus) {
                    connectionStatus.textContent = 'Connected - Live';
                    connectionStatus.style.color = '#4ade80';
                }
                if (statusDot) statusDot.classList.add('connected');
                if (statusText) statusText.textContent = 'Live';
                
                resolve(remoteStream);
            });
            
            call.on('close', () => {
                console.log('Host ended screen sharing');
                if (window.showToast) window.showToast('Host ended screen sharing', 'info');
                const connectionStatus = document.getElementById('connectionStatus');
                if (connectionStatus) connectionStatus.textContent = 'Host stopped sharing';
                
                const statusDot = document.getElementById('statusDot');
                const statusText = document.getElementById('statusText');
                if (statusDot) statusDot.classList.remove('connected');
                if (statusText) statusText.textContent = 'Disconnected';
            });
            
            call.on('error', (err) => {
                console.error('Call error:', err);
                reject(err);
            });
        });
        
        guestPeer.on('error', (err) => {
            console.error('Guest peer error:', err);
            reject(err);
        });
    });
}
"""
    with open(os.path.join(base_dir, "assets", "js", "webrtc.js"), "w", encoding="utf-8") as f:
        f.write(webrtc_js.strip())

    chat_js = """
import { db, collection, addDoc, onSnapshot, query, orderBy, limit, serverTimestamp } from './firebase-config.js';

export function initChat(roomId, isGuest) {
    let lastCommentTime = 0;
    const COOLDOWN_MS = 3000;
    let userId = localStorage.getItem('raffle_user_id') || ('anon_' + Math.random().toString(36).substr(2, 9));
    localStorage.setItem('raffle_user_id', userId);

    const savedNick = localStorage.getItem('raffle_nickname');
    if (savedNick && document.getElementById('feedback-nickname')) {
        document.getElementById('feedback-nickname').value = savedNick;
    }
    if (savedNick && document.getElementById('feedbackNickname')) {
        document.getElementById('feedbackNickname').value = savedNick;
    }

    // Always use the global collection to satisfy Firestore rules
    const commentsCollection = collection(db, 'raffle_comments');
    const q = query(commentsCollection, orderBy("timestamp", "asc"), limit(50));
    
    onSnapshot(q, (snapshot) => {
        const msgContainer = document.getElementById('feedback-messages') || document.getElementById('feedbackList');
        if (!msgContainer) return;
        
        msgContainer.innerHTML = '';
        
        const comments = [];
        snapshot.forEach(doc => {
            const data = doc.data();
            // Filter comments by roomId (or show global comments if no room specified)
            if (data.roomId === roomId || !data.roomId) {
                comments.push(data);
            }
        });
        
        if (comments.length === 0 && document.getElementById('feedback-messages')) {
            msgContainer.innerHTML = '<p class="feedback-placeholder">No comments yet. Be the first to drop a message!</p>';
            return;
        }

        comments.forEach(data => {
            const msgDiv = document.createElement('div');
            
            if (isGuest && document.getElementById('feedbackList')) {
                msgDiv.className = 'feedback-item';
                msgDiv.innerHTML = `
                    <div class="feedback-nickname">${escapeHTML(data.nickname || 'Anonymous')}</div>
                    <div class="feedback-text">${escapeHTML(data.text)}</div>
                `;
            } else {
                msgDiv.className = 'feedback-msg';
                let timeStr = data.timestamp ? (data.timestamp.toDate ? data.timestamp.toDate().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : '') : '';
                msgDiv.innerHTML = `<span class="time">${timeStr}</span><span class="nick">${escapeHTML(data.nickname)}:</span> ${escapeHTML(data.text)}`;
            }
            msgContainer.appendChild(msgDiv);
        });
        
        msgContainer.scrollTop = msgContainer.scrollHeight;
    });

    const submitBtn = document.getElementById('feedback-submit') || document.getElementById('sendFeedbackBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', () => {
            const nickInput = document.getElementById('feedback-nickname') || document.getElementById('feedbackNickname');
            const textInput = document.getElementById('feedback-text') || document.getElementById('feedbackText');
            
            let nickname = nickInput.value.trim();
            const text = textInput.value.trim();
            const cooldownMsg = document.getElementById('feedback-cooldown');

            if (!text) {
                alert("Please enter a comment.");
                return;
            }

            if (!nickname) {
                const anonCount = parseInt(localStorage.getItem('anon_comment_count') || '0') + 1;
                nickname = `Anonymous-${anonCount}`;
                localStorage.setItem('anon_comment_count', anonCount.toString());
                nickInput.value = nickname;
            }
            
            const now = Date.now();
            if (now - lastCommentTime < COOLDOWN_MS) {
                if (cooldownMsg) cooldownMsg.style.display = 'block';
                else alert('Please wait before sending another message');
                return;
            }
            if (cooldownMsg) cooldownMsg.style.display = 'none';

            localStorage.setItem('raffle_nickname', nickname);
            submitBtn.disabled = true;
            lastCommentTime = now;
            setTimeout(() => { submitBtn.disabled = false; }, COOLDOWN_MS);

            addDoc(commentsCollection, {
                text: text, 
                nickname: nickname, 
                userId: userId, 
                roomId: roomId,
                timestamp: serverTimestamp(),
                type: isGuest ? 'guest' : 'host'
            }).then(() => {
                textInput.value = '';
            }).catch(err => {
                console.error("Error posting comment: ", err);
                alert("Failed to send message.");
                submitBtn.disabled = false;
            });
        });
    }
}

function escapeHTML(str) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}
"""
    with open(os.path.join(base_dir, "assets", "js", "chat.js"), "w", encoding="utf-8") as f:
        f.write(chat_js.strip())

    # Extract the main script from index.html (the IIFE script logic)
    # We will strip out the Firebase and WebRTC parts that we moved, but keep the UI parts.
    # The IIFE script in index.html starts at <script> and ends at </script>
    
    scripts = re.findall(r'<script.*?>(.*?)</script>', index_content, re.DOTALL)
    # We assume the main UI logic is in the last script block, let's just grab the one with `function init()`
    main_logic = ""
    for script in scripts:
        if "function init()" in script or "function saveState()" in script:
            main_logic = script
            break

    # To avoid syntax errors due to duplicate `showToast` or other issues,
    # we just write this out to main.js, and import our new modules at the top.
    
    # Let's remove the <script> tags entirely from the HTML.
    index_content = re.sub(r'<script.*?</script>', '', index_content, flags=re.DOTALL)
    guest_content = re.sub(r'<script.*?</script>', '', guest_content, flags=re.DOTALL)
    
    # Add PeerJS to both
    peerjs_tag = '<script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>'
    
    # We will append the module imports
    index_content = index_content.replace('</body>', f'{peerjs_tag}\\n<script type="module" src="assets/js/main.js"></script>\\n</body>')
    guest_content = guest_content.replace('</body>', f'{peerjs_tag}\\n<script type="module" src="assets/js/guest.js"></script>\\n</body>')
    
    # We need to construct main.js
    # We will just write a simpler wrapper for main.js that includes what was there but imports chat.js and webrtc.js
    
    # Since extracting the exact main_logic via regex and patching it is risky, let's write a python script to patch main_logic string
    main_logic = main_logic.replace("window.startScreenShare = async function", "window.oldStartScreenShare = async function")
    main_logic = main_logic.replace("window.stopScreenShare = async function", "window.oldStopScreenShare = async function")
    main_logic = main_logic.replace("window.joinAsGuest = async function", "window.oldJoinAsGuest = async function")
    
    new_main_js = f"""
import {{ startScreenShare, stopScreenShare, joinAsGuest }} from './webrtc.js';
import {{ initChat }} from './chat.js';
import {{ db, doc, setDoc, onSnapshot, serverTimestamp, increment }} from './firebase-config.js';

window.startScreenShare = startScreenShare;
window.stopScreenShare = stopScreenShare;
window.joinAsGuest = joinAsGuest;

// We assign increment to window because main_logic might use it
window.increment = increment;
window.db = db;
window.doc = doc;
window.setDoc = setDoc;
window.serverTimestamp = serverTimestamp;

{main_logic}

// Wait for DOM to init
document.addEventListener('DOMContentLoaded', () => {{
    const urlParams = new URLSearchParams(window.location.search);
    const roomId = urlParams.get('room') || state.sessionId;
    const role = urlParams.get('role');
    const isGuest = role === 'guest';
    initChat(roomId, isGuest);
}});
"""
    with open(os.path.join(base_dir, "assets", "js", "main.js"), "w", encoding="utf-8") as f:
        f.write(new_main_js.strip())

    guest_js = """
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
"""
    with open(os.path.join(base_dir, "assets", "js", "guest.js"), "w", encoding="utf-8") as f:
        f.write(guest_js.strip())

    # Write back the HTML files
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)
        
    with open(guest_path, "w", encoding="utf-8") as f:
        f.write(guest_content)
        
if __name__ == "__main__":
    main()
