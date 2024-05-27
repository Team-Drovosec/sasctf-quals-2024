<?php

function download_handler($uuid) {
    if (is_uuid($uuid)) {
        chdir('/uploads/');
        $files = glob($uuid.'.*');
        if (sizeof($files) == 1) {
            $parts = explode('.', $files[0]);
            $fname = $parts[0].'.'.$parts[1];
            header('Content-Disposition: attachment; filename="'.$fname.'"');
            return file_get_contents('/uploads/'.$files[0]);
        }
    }
    return 'File not found or expired!';
}
?>