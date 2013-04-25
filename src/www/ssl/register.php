<?php
$TITLE = "SEAL - Request an Account";
$HEADER = "Request an Account";
include 'header.php';

if ($_SERVER['REQUEST_METHOD'] == "POST" &&
isset($_POST['uniqname']) && !empty($_POST['uniqname']))
{

	// NOTE: The functionalities for eecsverify.py
	// have been ported over to reduce clutter.
	$uniqname = $_POST['uniqname'];

	// Simple check for uniqname validity.
	if (preg_match("/^[a-zA-Z0-9]+$/", $uniqname))
	{
		function genRandomString($length) {
		    $characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
		    $string = '';    

		    for ($p = 0; $p < $length; $p++) {
		        $string .= $characters[mt_rand(0, strlen($characters))];
		    }

		    return $string;
		}

		$vcode = genRandomString(64);

		$db = new PDO('sqlite:/home/john/cloak/data/cloakdb');
		$stmt = $db->prepare("INSERT OR REPLACE INTO verification (veristring, uniqname) VALUES (?, ?)");
		if ( $stmt->execute( array($vcode, $uniqname) ) )
		{
			$cmd = '../webscripts/verimail.py '.$uniqname.' '.$vcode;
			$output = `$cmd`;
			if (empty($output))
			{
				echo 'Your verification email has been sent.
				Go to your University of Michigan inbox and
				follow the link in the email to continue
				creating your SEAL account.';
			}
		}
		else
		{
			echo 'Database error';
		}

	}
	else
	{
		echo "<font color=\"red\"><b>Missing or invalid uniqname!</b></font><br>";
		include 'veriform.php';
	}
	
}
else
{
	echo "<font color=\"red\"><b>SEAL is currently being made available only to people
	holding a University of Michigan uniqname and corresponding email account.
	<br><br> Please follow this brief verification process before creating your
	account.</b></font>
	<br><br>";
	include 'veriform.php';
}
include 'navi.php';
include 'footer.php';
?>
