<html>
<head>
<title>Cloak Contact Email Page</title>
</head>
<body>
Welcome to the <?php echo $_SERVER["SERVER_NAME"]; ?> contact page!
<br><br>
You can contact us at our email: 
<?php
$ip_addr = $_SERVER["REMOTE_ADDR"];
$domain  = $_SERVER["SERVER_NAME"];
$alias = `/home/john/cloak/src/Scripts/tools/genalias.py $ip_addr $domain`;
$arr = explode("\n", $alias);
?>
<a href="mailto:<?php echo $arr[1]; ?>">
<?php echo $arr[1]; ?></a> for more information.

<?php
/*
<!--

Actual IP: <?php echo $ip_addr; ?

Decoded IP: <?php echo $arr[2]; ?

-->
*/
?>

<h3>Alternative Contacts</h3>
You can also contact us at <a href:"mailto:cloak.cq94v593@cloak.dyndns-mail.com">cloak.cq94v593@cloak.dyndns-mail.com</a> or <img src="altcontact1.png" width="20%"/>.

</body>
</html>

