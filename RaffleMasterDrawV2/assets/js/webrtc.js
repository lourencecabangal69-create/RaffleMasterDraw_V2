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