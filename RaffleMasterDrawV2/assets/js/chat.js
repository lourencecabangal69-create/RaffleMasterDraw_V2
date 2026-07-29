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