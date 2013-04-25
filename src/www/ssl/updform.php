<br>	
<table>
	<form id="upduser" name="upduser" action="update.php" method="post">
	<tr>
		<td>Forwarding Address:</td>
		<td><input type="text" name="fwdaddx" size="30" value="<?php
			$uid = $_SESSION['uid'];
			$db = new PDO("sqlite:/home/john/cloak/data/cloakdb");
			$result = $db->query("SELECT fwdaddr FROM `user` WHERE uid='$uid'");
			$row = $result->fetch();
			echo $row['fwdaddr'];
			?>">
		<input type="hidden" name="uid" value="<?php echo $_SESSION['uid']?>">
		</td>
	</tr>
	<tr>
		<td></td>
		<td><input type="submit" name="upduserButton" value="Update Forwarding Address"></td>
	</tr>
	</form>

	<tr><td><br></td></tr>

	<form id="updpwd" name="updpwd" action="update.php" method="post">

	<tr>
		<td>Old Password:</td>
		<td><input type="password" name="password" size="30" value=""></td>
	</tr>
	<tr>
		<td>New Password:</td>
		<td><input type="password" name="newpwd" size="30" value=""></td>
	</tr>
	<tr>
		<td>Retype Password:</td>
		<td><input type="password" name="newpwd2" size="30" value="">
		<input type="hidden" name="uid" value="<?php echo $_SESSION['uid']?>"></td>
	</tr>
	<tr>
		<td></td>
		<td><input type="submit" name="updpwdButton" value="Update Password"></td>
	</tr>
	</form>
</table>


