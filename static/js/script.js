function toggleMenu() {
    var navLinks = document.getElementById("navLinks");
    if (navLinks.style.display === "flex") {
        navLinks.style.display = "none";
    } else {
        navLinks.style.display = "flex";
    }
}
function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");
    var icon = document.getElementById("darkModeIcon");
    if (document.body.classList.contains("dark-mode")) {
       icon.classList.remove("fa-moon");
       icon.classList.add("fa-sun"); 
    }else {
        icon.classList.remove("fa-sun");
        icon.classList.add("fa-moon");
    }
}
document.querySelector('.upload-btn').addEventListener('click', function() {
    document.getElementById('uploadInput').click();
});

function previewImage(event) {
    const input = event.target;
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            document.body.appendChild(img);
        }
        reader.readAsDataURL(input.files[0]);
    }
}

document.querySelector('.photo-btn').addEventListener('click', function() {
    openCamera();
});

function openCamera() {
    const video = document.getElementById('camera');
    const canvas = document.getElementById('canvas');
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true }).then(function(stream) {
            video.srcObject = stream;
            video.style.display = 'block';
            canvas.style.display = 'block';
        }).catch(function(error) {
            alert("Camera access denied or not available.");
        });
    } else {
        alert("Camera not supported by your browser.");
    }
}

function takePhoto() {
    const video = document.getElementById('camera');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imgData = canvas.toDataURL('image/png');
    const img = document.createElement('img');
    img.src = imgData;
    document.body.appendChild(img);
}

document.querySelector('.prompt-btn').addEventListener('click', function() {
    const promptValue = document.querySelector('.prompt-bar').value;
    alert('Prompt entered: ' + promptValue);
});
