document.addEventListener("DOMContentLoaded", fetchFiles);

function fetchFiles() {
    const searchInput = document.getElementById('searchInput').value;
    fetch(`/api/data?name=${searchInput}`)
        .then(response => response.json())
        .then(files => displayFiles(files));
}

function displayFiles(files) {
    const fileList = document.getElementById('fileList');
    fileList.innerHTML = '';
    files.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.textContent = file.filename;
        fileItem.onclick = () => displayContent(file.content);
        fileList.appendChild(fileItem);
    });
}

function displayContent(content) {
    const jsonContent = document.getElementById('jsonContent');
    jsonContent.innerHTML = JSON.stringify(content, null, 4);
}
