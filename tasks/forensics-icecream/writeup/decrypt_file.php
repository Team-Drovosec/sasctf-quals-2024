<?php

  $fbe_key = hex2bin("23da98d7147e0cb94ca5410cf54d618d08967bb40dbd4ebc1ef759e8fbacfe1ea49c72177291a76cb6478e717e42c7c3e2b8236f603bf00ef2b140dbdef13c21");
  $dir_nonce = hex2bin("E00B4120947002C467C0544A7E90B7F0");
  $bs_enc = 512;

  $userdata_start = 15253504*512;

  $files = array(
    0x000805B4 => array(
      "offset"=>0x20911D000,
      "size"=>35,     
      "name"=>hex2bin("61CD818B2524418697153528AB1842B5")
    ),
  );
  
  $dir_key = openssl_encrypt(substr($fbe_key, 0, 32), 'aes-128-ecb', $dir_nonce, OPENSSL_RAW_DATA | OPENSSL_ZERO_PADDING);
  $file_key = $fbe_key;

  $dir_iv = pack("V4", 0, 0, 0, 0);
  foreach($files as $inode=>$file)
  {
    $fname = $file["name"];
    $fname = decrypt_filename($fname, $dir_key, $dir_iv);
    printf("0x%08x - %s\n", $inode, $fname);

    $fname_enc = sprintf("0x%08x", $inode);
    if (!file_exists($fname_enc)) continue;
    $s = file_get_contents($fname_enc);
    $r = openssl_decrypt($s, 'aes-256-xts', $file_key, OPENSSL_RAW_DATA | OPENSSL_ZERO_PADDING, pack("V4", intdiv($userdata_start+$file['offset'], $bs_enc), 0, 0, 0));
    file_put_contents($fname, substr($r, 0, $file['size']));
  }

  function decrypt_filename($name, $key, $iv)
  {
    if (strlen($name) < 16) return false;
    if (strlen($name) == 16) $name = openssl_decrypt($name, 'aes-256-cbc', $key, OPENSSL_RAW_DATA | OPENSSL_ZERO_PADDING, $iv);
    else $name = decrypt_aes_cbc_cts2($name, $key, $iv);
    
    $name = rtrim($name, "\x00");
    return $name;
  }

  function decrypt_aes_cbc_cts2($data, $key, $iv)
  {
    $l = strlen($data);
    $l2 = $l & 0xf;
    if ($l2 == 0) $l2 = 16;

    $a = substr($data, 0, $l-$l2-16);
    $b = substr($data, -16-$l2, 16);
    $c = substr($data, -$l2);

    $b = openssl_decrypt($b, 'aes-256-ecb', $key, OPENSSL_RAW_DATA | OPENSSL_ZERO_PADDING);
    $d = ($l2 == 16)?"":substr($b, $l2-16);
    $e = $c ^ $b;
    $a = openssl_decrypt($a.$c.$d, 'aes-256-cbc', $key, OPENSSL_RAW_DATA | OPENSSL_ZERO_PADDING, $iv);
    return $a.$e;
  }

