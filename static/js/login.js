// Toggle password visibility
function togglePassword() {
    const pwd = document.getElementById('password');
    const icon = document.querySelector('.toggle-password');
    if (pwd.type === 'password') {
        pwd.type = 'text';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    } else {
        pwd.type = 'password';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    }
}

// Loading animation on form submit
document.getElementById('loginForm').addEventListener('submit', function(e) {
    const btn = document.getElementById('loginBtn');
    btn.querySelector('span').style.display = 'none';
    btn.querySelector('.fa-spinner').style.display = 'inline-block';
});

// Face Login Modal
const modal = document.getElementById('faceModal');
const faceBtn = document.getElementById('faceLoginBtn');
const closeBtn = document.querySelector('.close');
const captureBtn = document.getElementById('captureBtn');
const video = document.getElementById('video');
const faceStatus = document.getElementById('faceStatus');
let stream = null;

faceBtn.onclick = function() {
    modal.style.display = 'flex';
    startCamera();
};

closeBtn.onclick = function() {
    modal.style.display = 'none';
    stopCamera();
};

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = 'none';
        stopCamera();
    }
};

function startCamera() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(s => {
            stream = s;
            video.srcObject = stream;
        })
        .catch(err => {
            faceStatus.innerHTML = '<span style="color:red;">Camera access denied</span>';
        });
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
    }
}

captureBtn.addEventListener('click', function() {
    if (!video.videoWidth) {
        faceStatus.innerHTML = '<span style="color:red;">Camera not ready</span>';
        return;
    }
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataURL = canvas.toDataURL('image/jpeg');

    faceStatus.innerHTML = 'Recognizing...';

    fetch('/face-login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: dataURL })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            faceStatus.innerHTML = '<span style="color:green;">Login successful! Redirecting...</span>';
            window.location.href = data.redirect;
        } else {
            faceStatus.innerHTML = '<span style="color:red;">' + data.message + '</span>';
        }
    })
    .catch(err => {
        faceStatus.innerHTML = '<span style="color:red;">Error: ' + err + '</span>';
    });
});