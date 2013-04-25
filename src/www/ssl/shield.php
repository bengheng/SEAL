<?php
require 'aes.class.php';
require 'aesctr.class.php';
function get_ip_address() {
  foreach (array('HTTP_CLIENT_IP', 'HTTP_X_FORWARDED_FOR', 'HTTP_X_FORWARDED', 'HTTP_X_CLUSTER_CLIENT_IP', 'HTTP_FORWARDED_FOR', 'HTTP_FORWARDED', 'REMOTE_ADDR') as $key) {
    if (array_key_exists($key, $_SERVER) === true) {
      foreach (explode(',', $_SERVER[$key]) as $ip) {
        if (filter_var($ip, FILTER_VALIDATE_IP) !== false) {
          return $ip;
        }
      }
    }
  }
}
$sk = "ODk3MzIyMTA=";
$dat = array(
    "user" => "bengheng",
    "domain" => get_ip_address(),
    "alias" => "",
    "hint" => ""
);
$req = array(
    "user" => "bengheng",
    "w" => "185",
    "c" => AesCtr::encrypt( json_encode($dat), $sk, 256)
);
$r = new HttpRequest('https://'.$_SERVER['SERVER_NAME'].'/cgi-bin/getalias.py?r='.base64_encode( json_encode($req) ), HttpRequest::METH_GET);
  $r->setContentType = 'Content-Type: text/html';
  try {
      $r->send();
      if ($r->getResponseCode() == 200) {
          $email = $r->getResponseBody();
      }
      else {
          echo "Error ".$r->getResponseCode();
      }
  } catch (HttpException $ex) {
      echo $ex;
  }
?>

