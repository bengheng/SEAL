<?php
$TITLE = "SEAL - Account Creation";
$HEADER = "Account Creation";
include 'header.php';
?>

<br>

<form id="createaccount" name="createaccount" action=
"../cgi-bin/eecsadd.py" method="post">
	<input type="hidden" name="mailverify" id="mailverify" value="<?php if(isset($_GET["mail"])) echo htmlentities($_GET["mail"],ENT_QUOTES); ?>" />
	<table border="0" cellpadding="2" cellspacing="0">
		<tr>
		<td valign="top" nowrap="nowrap"><font size=
		"-1"><b>Desired Account Name:</b></font>
		<b>&nbsp;</b></td>

		<td dir="ltr"><bdo dir="ltr"><input type="text" name=
		"username" id="username" size="30" value=""></bdo>
		<font size="-2" color="#6F6F6F">Examples: jsmith,
		JohnSmith</font></td>

		<td valign="top" nowrap="nowrap"><bdo dir=
		"ltr"><font size=
		"-1"><i>@<?php echo $_SERVER["SERVER_NAME"]; ?></i></font></bdo></td>
		</tr>

		<tr><td><br></td></tr>

		<tr>
		<td valign="top" nowrap="nowrap"><font size=
		"-1"><b>Choose a password:</b></font></td>

		<td valign="top"><input type="password" name="passwd"
		id="passwd" size="30"><br>
		<font size="-2" color="#6F6F6F">Minimum of 8
		characters in length.</font></td>
		</tr>

		<tr><td><br></td></tr>

		<tr>
		<td valign="top" nowrap="nowrap"><font size=
		"-1"><b>Re-enter password:</b></font></td>

		<td><input type="password" name="passwdagain" id=
		"passwdagain" size="30"></td>
		</tr>

		<tr><td><br></td></tr>

		<tr>
		<td valign="top" nowrap="nowrap"><font size=
		"-1"><b>Forwarding email:</b></font></td>

		<td><input type="text" name="fwdaddx" id="fwdaddx"
		size="30" value=""><br>
		<font size="-2" color="#6F6F6F">This address is used
		to forward any emails you may receive and to send any
		error messages issued by your use of the
		service.</font></td>
		</tr>

		<tr><td><br></td></tr>

		<tr><td><br></td></tr>

		<tr>
		<td colspan="1">&nbsp;</td>

		<td align="center"><input id="submitbutton" name=
		"submitbutton" style="width:10em" type="submit"
		value="Submit"></td>
		</tr>
	</table>

</form>

<?php
include 'footer.php';
?>
