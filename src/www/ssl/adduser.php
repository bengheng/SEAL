<?php
function accountname_exists($db, $acctname)
{
	$acctexists = FALSE;
	try
	{
		$stmt = $db->prepare( "SELECT COUNT(*) FROM user WHERE username=?" );
		$stmt->execute( array( $acctname ) );
		$row = $stmt->fetch();

		if ( $row[0] != 0 )
		{
			$acctexists = TRUE;
		}
	}
	catch (Exception $e)
	{
		echo $e->getMessage();
	}

	return $acctexists;
}

function mailverify_exist($db, $vcode)
{
	$nrows = 0;
	$uniqname = "";
	try
	{
		$stmt = $db->prepare( "SELECT uniqname FROM verification WHERE veristring=?" );
		$stmt->execute( array( $vcode ) );
		$row = $stmt->fetch();

		if ( $row )
		{
			$uniqname = $row['uniqname'];
		
		}

		else
		{
			$uniqname = '';
		}
	}
	catch (Exception $e)
	{
		echo $e->getMessage();
	}

	if($uniqname != "")
	{
		return TRUE;
	}

	return FALSE;
}

function mailverify_is_valid($db, $vcode)
{
	$nrows = 0;
	$uniqname = "";
	try
	{
		$stmt = $db->prepare( "SELECT uniqname FROM verification WHERE veristring=?" );
		$stmt->execute( array( $vcode ) );
		$row = $stmt->fetch();

		if ( $row )
		{
			$uniqname = $row['uniqname'];
		
		}

		else
		{
			$uniqname = '';
		}

		$nrows = $db->exec( "DELETE FROM verification WHERE veristring=\"".$vcode."\";" );
	}
	catch (Exception $e)
	{
		echo $e->getMessage();
	}

	if($nrows == 1 && $uniqname != "")
	{
		return $uniqname;
	}
	else
	{
		return FALSE;
	}
}

function is_valid_email( $email )
{
	return ( preg_match("^.+@.+\..{2,3}$", $email) == 1 );
}

function add_user($db, $usrname, $pwd, $fwdaddr, $salt, $retrievalkey, $uniqname)
{
	$res = FALSE;
	$uid = -1;
	try
	{
		$stmt = $db->prepare( "INSERT OR FAIL INTO `user`
			(`username`, `spwd`, `fwdaddr`, `salt`, `retrievalkey`, `uniqname`) VALUES
			(?, ?, ?, ?, ?, ?);" );

		$res = $stmt->execute(array($usrname,$pwd,$fwdaddr,$salt,$retrievalkey,$uniqname));
		if ($res)
		{
			$uid = $db->lastInsertId('uid');
		}
	}
	catch (Exception $e)
	{
		echo $e->getMessage();
	}

	return $uid;
}

function genRandomString($length) {
	$characters =
'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
	$string = '';
	for ($p = 0; $p < $length; $p++) {
		$string .= $characters[mt_rand(0, strlen($characters))];
	}
	return $string;
}

if($_SERVER["REQUEST_METHOD"] == "POST")
{
	$errmsg = "";
	$username = "";
	$passwd = "";
	$passwdagain = "";
	$fwdaddx = "";
	$mailverify = "";

	// Get all variables first

	if (isset($_POST['username']) && !empty($_POST['username']))
	{
		$username = addslashes($_POST['username']);
	}
	if (isset($_POST['passwd']) && !empty($_POST['passwd']))
	{
		$passwd = $_POST['passwd'];
	}
	if (isset($_POST['passwdagain']) && !empty($_POST['passwdagain']))
	{
		$passwdagain = $_POST['passwdagain'];
	}
	if (isset($_POST['fwdaddx']) && !empty($_POST['fwdaddx']))
	{
		$fwdaddx = addslashes($_POST['fwdaddx']);
	}
	if (isset($_POST['mailverify']) && !empty($_POST['mailverify']))
	{
		$mailverify = addslashes($_POST['mailverify']);
	}

	/////////////////
	// Verifications
	/////////////////

	$db = new PDO("sqlite:/home/john/cloak/data/cloakdb");

	// Accountname
	if ( $username == "" )
	{
		$errmsg .= "<li>Missing account name.</li>";
	}
	elseif ( accountname_exists($db, $username) )
	{
		$errmsg .= "<li>Account name already taken.</li>";
	}

	// Password
	if ( $passwd == "" )
	{
		$errmsg .= "<li>Missing password.</li>";
	}
	elseif ( strlen($passwd) < 8 )
	{
		$errmsg .= "<li>Password must have at least 8 characters.</li>";
	}

	if ( $passwdagain == "" )
	{
		$errmsg .= "<li>Did not re-type password.</li>";
	}

	if ( $passwd <> "" && ($passwd <> $passwdagain) )
	{
		$errmsg .= "<li>Passwords did not match.</li>";
	}

	if($errmsg == "")
	{
		$uniqname = mailverify_is_valid($db, $mailverify);

		if(!$uniqname)
			{
				$errmsg .= "<li>Could not find verification string. Either you forgot to
				request a verification string <a href=\"register.php\">here</a> or the
				verification string has already been used to register an account.</li>";
			}
	}

	// Forwarding address
	if ( $fwdaddx == "" )
	{
		$errmsg .= "<li>Missing forwarding address.</li>";
	}

	// If any error, output error messages.
	if ( $errmsg <> "" )
	{
		$TITLE = "SEAL - Account Creation";
		$HEAER = "Account Creation";
		include 'header.php';
		echo "<font color=\"red\">";
		echo "<ol>".$errmsg."</ol>";
		echo "</font>";
		include 'regform.php';
		include 'footer.php';
	}
	else
	{
		// Otherwise inputs are ok, login user.

		// Prepare password
		$hashedpwd = "{PLAIN-MD5}".md5($passwd);

		// Salt
		$salt = genRandomString(64);

		// Retrieval key
		$retrievalkey = genRandomString(64);

		$uid = add_user( $db,
			$username,
			$hashedpwd,
			$fwdaddx,
			$salt,
			$retrievalkey,
			$uniqname );
		if ($uid != -1)
		{
			session_start();
			$_SESSION['user'] = $username;
			$_SESSION['uid'] = $uid;

			$TITLE = "SEAL - Account Creation";
			$HEADER = "Account Creation Successful";
			include 'header.php';

			echo "Account created successfully.<br>
				<b>Remember to <a href=\"getalias.php\">create a SEAL alias</a> 
				for distribution to your contacts!</b>";

			// Send email to user.
			$cmd = "../webscripts/acctcreated.py ".$_POST['username'];
			echo `$cmd`;

			include 'navi.php';
			include 'footer.php';
		}
	}

}
else
{
	$TITLE = "SEAL - Account Creation";
	$HEADER = "Account Creation";
	include 'header.php';

	if($_POST['mailverify'] <> "")
		$mailverify = $_POST['mailverify'];
	else
		$mailverify = $_GET['mailverify'];

	$db = new PDO("sqlite:/home/john/cloak/data/cloakdb");
	if ( mailverify_exist($db, $mailverify)  == FALSE )
	{
?>
	The verification string is invalid. Please request a valid verification
string <a href="register.php">here</a> and try again.


<?php
	include 'navi.php';
	}
	else
	{
	?>

	Please fill in all of the information below.<br><br> Note that your forwarding email address can be any
address you choose (including a non-University of Michigan address).  We highly recommend creating a new account on <a
href="http://mail.google.com">Gmail</a> to use as your forwarding email
address.<br><br>
<font color="red">IMPORTANT!<br>
Please note that successful registration <b>does not</b> mean you will
immediately have an email address that you can distribute to others. <b>An
alias is not your account name!</b> To get an email address that can be
distributed to others, you must get an alias. You will be guided through the
simple process for creating an alias immediately after completing this registration
form.</font><br>

<?php
	include 'regform.php';
	}

	include 'footer.php';
}

?> 
