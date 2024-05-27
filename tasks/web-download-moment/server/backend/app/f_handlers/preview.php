<?php

function preview_handler($uuid) {

    function prepare_image_preview($path) {
        $img = imagecreatefromstring(file_get_contents($path));
        if ($img){
            $size = getimagesize($path);
            if ($size[0] <= MAX_DIM && $size[1] <= MAX_DIM){
                ob_start();
                imagepng($img);
                $data = ob_get_contents();
                ob_end_clean();
            } else {
                $ratio = $size[0] / $size[1];
                $new_width = $ratio > 1 ? MAX_DIM : MAX_DIM * $ratio;
                $new_height = $ratio > 1 ? MAX_DIM / $ratio : MAX_DIM;
                $dst = imagecreatetruecolor($new_width, $new_height);
                imagecopyresampled($dst, $img, 0, 0, 0, 0, $new_width, $new_height, $size[0], $size[1]);

                ob_start();
                imagepng($dst);
                $data = ob_get_contents();
                ob_end_clean();

                imagedestroy($dst);
            }
            imagedestroy($img);
            return array("type" => "image", "content" => "data:image/png;base64,".base64_encode($data));
        } else {
            return fail();
        }
    }
    
    function prepare_zip_preview($path) {
        $zip = new ZipArchive;
        if ($zip->open($path) === true) {
            if (isDestructiveArchive($zip)) {
                $zip->close();
                return fail();
            }
            $ret = array("type" => "zip", "content" => array());
            $temp_dir = '/tmp/'.get_uuid();
            $zip->extractTo($temp_dir);
            chdir($temp_dir);
            for ($idx = 0; $file = $zip->statIndex($idx); $idx++) {
                $name = $file['name'];
                $ext = pathinfo($name, PATHINFO_EXTENSION);
        
                if (is_dir($name)) {
                    array_push($ret['content'], array("type" => "dir", "filename" => $name));
                } else if (getimagesize($name)) {
                    array_push($ret['content'], array_merge(prepare_image_preview($name), array("filename" => $name)));
                } else {
                    array_push($ret['content'], array_merge(prepare_text_preview($name), array("filename" => $name)));
                }
            }
            $zip->close();
            system('rm -rf '.$temp_dir);
            return $ret;
        } else {
            return fail();
        }
    }
    
    function prepare_text_preview($path) {
        $fp = fopen($path, 'r');
        if (!$fp) {
            return fail();
        }
        $data = fread($fp, TEXT_PREVIEW_LENGTH);
        fclose($fp);

        if (preg_match('/[^\x20-\x7E\r\n\t]/', $data) > 0) {
            return fail();
        } else {
            return array("type" => "text", "content" => $data.'...');
        }
    }
    
    function fail() {
        return array("type" => "text", "content" => "Can't generate preview for this file!");
    }

    if (is_uuid($uuid)) {
        chdir('/uploads/');
        $files = glob($uuid.'.*');
        if (sizeof($files) == 1) {
            $ext = explode('.', $files[0])[1];
            $info = array();
            $info['time_left'] = max(FILE_LIFETIME - (time() - filectime($files[0])), 0);
            $info['size'] = filesize($files[0]);
            if (getimagesize($files[0])) {
                $preview = prepare_image_preview($files[0]);
            } else if ($ext === 'zip') {
                $preview = prepare_zip_preview($files[0]);
            } else {
                $preview = prepare_text_preview($files[0]);
            }
            return json_encode(array_merge($preview, $info));
        }
    }
    return 'ERR:File not found or expired!';
}

function isDestructiveArchive($zip) {
    for ($idx = 0; $file = $zip->statIndex($idx); $idx++) {
        if ($idx > MAX_ZIP_ENTRIES || $file['size'] > MAX_SIZE_PER_ZIP_ENTRY){
            return true;
        }
    }
    return false;
}

?>