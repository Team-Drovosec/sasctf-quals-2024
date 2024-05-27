<?php

function upload_handler() {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        return 'ERR:Method not supported!';
    }

    if (!isset($_FILES['file'])) {
        return 'ERR:No file provided!';
    }

    $uuid = get_uuid();
    $ext = pathinfo($_FILES['file']['name'], PATHINFO_EXTENSION);
    $ext = $ext ? $ext : 'txt';
    if(move_uploaded_file($_FILES['file']['tmp_name'], '/uploads/'.$uuid.'.'.$ext)){
        return $uuid;
    } else {
        return 'ERR:Upload failed!';
    }
}

?>