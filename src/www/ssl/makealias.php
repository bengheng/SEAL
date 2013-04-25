<?php
  ini_set('display_errors', 'On');
  error_reporting(E_ALL);

  require 'aes.class.php';     // AES PHP implementation
  require 'aesctr.class.php';  // AES Counter Mode implementation

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
  
  // initialise sessionkey & plaintesxt
  $sk = 'oLwLlFuyWWDb2V9cgenwBmc77jjvLGo5TRk2gQOIy3t0CCwCWrepZGGn/Ilc/uhrRV9UHNCAlfh8LHVye7Ck4Q==';
  $wid = 140;

  // Create request
  $dat = array(
    "user" => "bengheng",
    "domain" => get_ip_address(),
    "hint" => "a",
    "alias" => "a"
  );
  $req = array(
    "user" => "bengheng",
    "w" => $wid,
    "c" => AesCtr::encrypt( json_encode($dat), $sk, 256)
  );

  // Send request
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

<!DOCTYPE html>
<html lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>PHP Test Script for Making Alias</title>
</head>
<body>
<form name="frm" id="frm" method="post" action=""> <!-- same-document reference -->
  <table>  
    <tr>
      <td>Session Key: </td>
      <td><input type="text" name="sk" value="<?= $sk ?>"></td>
    </tr>
    <tr>
      <td>WID: </td>
      <td><input type="text" name="wid" value="<?= $wid ?>"></td>
    </tr>
 </table>
</form>

<p><?= $email ?></p>

</body>
</html>
