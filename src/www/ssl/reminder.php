<?php

$TITLE = "SEAL - Reset Password";
$HEADER = "Reset Password";
include 'header.php';

if ( $_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['username']) && !empty($_POST['username']) )
{
	$cmd = "../webscripts/reminder.py ".$_POST['username'];
	$result = `$cmd`;
	echo $result;
}
else
{
?>

<p>Please enter your username to request a new password. An email will be sent to
the forwarding address specified for your account.</p><br>

<form id="resetpwd" name="resetpwd" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="post">
<table>
<tr>
<td>
Username :
</td>
<td>
<input type="text" name="username" id="username" size="30" value="">
</td>
</tr>
<tr>
<td>
</td>
<td>
<input type="submit" id="submitButton" name="submitButton" style="width:10em" value="Reset Password">
</td>
</tr>
</table>
</form>

<?php
}

include 'navi.php';
include 'footer.php';
?>
