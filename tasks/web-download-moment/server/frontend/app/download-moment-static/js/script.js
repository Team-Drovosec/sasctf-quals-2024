let lastTarget;

document.getElementById('copy-icon').addEventListener('click', (event) => {
    navigator.clipboard.writeText(event.target.previousElementSibling.innerText);
});

document.querySelector('.logo-container').addEventListener('click', (event) => {
    window.location.assign('/');
});

function sendFile() {
    fetch("/upload", {
        body: new FormData(document.querySelector('form')),
        method: "POST"
    }).then((result) => {
        if (result.ok) {
            result.text().then((t) => {
                if (t.substr(0, 4) === 'ERR:') {
                    alert('Upload failed!');
                } else {
                    let url = window.location.protocol + '//' + window.location.hostname + (window.location.port ? (':' + window.location.port) : '') + '/' + t;
                    let text = document.getElementById('text-center');
                    text.querySelector('a').innerText = url;
                    text.querySelector('a').href = url;
                    window.upload.style = 'display: none';
                    text.style = '';
                }
            });
        } else {
            throw 1
        }
    }).catch((err) => {
        alert('Upload failed!');
    });
}

function showUploadPage() {
    window.addEventListener('dragenter', (event) => {
        event.preventDefault();
        lastTarget = event.target;
        window.dropzone.style.visibility = "";
        window.dropzone.style.opacity = 1;
    });
    
    window.addEventListener('dragleave', (event) => {
        if (event.target === lastTarget || event.target === document) {
            window.dropzone.style.visibility = 'hidden';
            window.dropzone.style.opacity = 0;
        }
    });

    window.addEventListener("dragover", (event) => {
        event.preventDefault();
    });
    
    window.addEventListener('drop', (event) => {
        event.preventDefault();
        window.dropzone.style.visibility = 'hidden';
        window.dropzone.style.opacity = 0;
        let files = event.dataTransfer.files;
        if (files.length > 1){
            return alert('One file at a time!');
        }
        if (files[0].size > 1048576){
            return alert('No more than 1MB per file!');
        }
        window.file.files = files;
        sendFile();
    });

    document.getElementById('drag-drop-area').addEventListener('click', (event) => {
        window.file.click();
    });

    window.file.onchange = (event) => {
        let files = window.file.files;
        if (files.length > 1){
            return alert('One file at a time!');
        }
        if (files[0].size > 1048576){
            return alert('No more than 1MB per file!');
        }
        sendFile();
    };

    window.upload.style = '';
}

function showMsg(msg) {
    let text = document.getElementById('text-center');
    text.innerText = msg;
    text.style = '';
}

function getPreview(id) {
    fetch('/preview/' + id).then((result) => {
        if (result.ok) {
            result.text().then((resp) => {
                if (resp.substr(0, 4) === 'ERR:') {
                    showMsg('File not found or expired!');
                } else {
                    showPreviewPage(id, resp);
                }
            });
        } else {
            throw 1
        }
    }).catch((err) => {
        showMsg('File not found or expired!');
    });
}

function addEntry(container, data) {
    let entry = document.createElement('div'), path = document.createElement('div'), content = document.createElement('div');
    entry.className = 'file-entry';
    path.className = 'file-path';
    path.innerText = data['filename'];
    if (data['type'] == 'image') {
        content.className = 'file-content';
        let img = new Image();
        img.src = data['content'];
        content.appendChild(img);
    } else if (data['type'] == 'dir'){
        // do nothing
    } else {
        content.className = 'file-content text-content';
        content.innerText = data['content'];
    }
    entry.appendChild(path); entry.appendChild(content);
    container.appendChild(entry);
}

function timer(el, cur) {
    el.innerText = Math.floor(cur / 60).toString().padStart(2, '0') + ":" + (cur % 60).toString().padStart(2, '0');

    if (--cur < 0) {
        window.location.assign('/');
    }

    return cur;
}

function setupTimer(el, time_left) {
    let cur = time_left;
    cur = timer(el, cur);
    setInterval(() => {cur = timer(el, cur)}, 1000);
}

function format_size(size) {
    let i = size == 0 ? 0 : Math.floor(Math.log(size) / Math.log(1024));
    return Math.ceil(size / Math.pow(1024, i)) + ['B', 'KB', 'MB'][i];
}

function showPreviewPage(id, resp) {
    data = JSON.parse(resp);
    preview_cont = document.querySelector('.file-list');
    if (data['type'] == 'zip') {
        for (file of data['content']) {
            addEntry(preview_cont, file);
        }
    } else {
        data['filename'] = id;
        addEntry(preview_cont, data);
    }
    setupTimer(document.querySelector('.time-remaining'), data['time_left']);
    document.querySelector('.file-size').innerText = format_size(data['size']);
    document.querySelector('.download-button').addEventListener('click', (event) => {
        window.open(window.location.protocol + '//' + window.location.hostname + (window.location.port ? (':' + window.location.port) : '') + '/download/' + id);
    });
    
    window.preview.style = '';
}

window.onload = () => {
    if (window.location.pathname === '/'){
        showUploadPage();
    } else {
        file_id = window.location.pathname.replaceAll('/', '');
        getPreview(file_id);
    }
}