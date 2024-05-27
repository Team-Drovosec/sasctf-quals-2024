<?php
function get_client_ip() {
    return $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['REMOTE_ADDR'] ?? $_SERVER['HTTP_CLIENT_IP'] ?? '';
}

if(isset($_GET['amount'])){
    $x = $_GET['amount'];
    $ip = ip2long(get_client_ip());
    $result = eval('return (int)((4 + abs(sin('.$ip.') + tan(intval("'.$x.'")) - sqrt(abs(intval("'.$x.'")))) / 100) * intval("'.$x.'"));');

    echo $result;
} else {
    echo 'Access Denied';
}
?>