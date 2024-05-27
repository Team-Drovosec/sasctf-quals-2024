var pc = null;
var dc = null;

game_audio = new Audio("sound.mp3");
game_audio.loop = true;
game_audio.volume = 0.5;

lose_audio = new Audio("lose.mp3");
lose_audio.loop = true;
lose_audio.volume = 0.5;

win_audio = new Audio("win.mp3");
win_audio.loop = true;
win_audio.volume = 0.5;

function negotiate() {
    pc.addTransceiver('video', { direction: 'recvonly' });
    pc.addTransceiver('audio', { direction: 'recvonly' });
    return pc.createOffer().then((offer) => {
        return pc.setLocalDescription(offer);
    }).then(() => {
        // wait for ICE gathering to complete
        return new Promise((resolve) => {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                const checkState = () => {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                };
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(() => {
        var offer = pc.localDescription;
        return fetch('/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then((response) => {
        return response.json();
    }).then((answer) => {
        game_audio.play()
        return pc.setRemoteDescription(answer);
    }).catch((e) => {
        alert(e);
    });
}

function start() {
    var config = {
        sdpSemantics: 'unified-plan'
    };

    pc = new RTCPeerConnection(config, {
      optional: [{
        RtpDataChannels: true
      }]
    });

    dc = pc.createDataChannel("DROVOSEC_GAME", {
      reliable: false
    });

    dc.onmessage = message => {
      data = message.data;
      if (data == "game_over") {
        game_audio.pause()
        lose_audio.play()
        document.getElementById('restart').style.display = 'block';
      }
      if (data == "game_win") {
        game_audio.pause()
        win_audio.play()
      }
    };

    document.addEventListener("keypress", function(event) {
      switch (event.code) {
      case 'KeyW':
        dc.send("W")
        break
      case 'KeyA':
        dc.send("A")
        break
      case 'KeyS':
        dc.send("S")
        break
      case 'KeyD':
        dc.send("D")
        break
      case 'Space':
        dc.send("attack")
        break
      }
    });

    // connect audio / video
    pc.addEventListener('track', (evt) => {
        if (evt.track.kind == 'video') {
            document.getElementById('video').srcObject = evt.streams[0];
        } else {
            document.getElementById('audio').srcObject = evt.streams[0];
        }
    });

    document.getElementById('start').style.display = 'none';
    negotiate();
}