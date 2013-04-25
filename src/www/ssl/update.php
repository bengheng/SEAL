<?php 
session_start();

$TITLE = "SEAL - Update User Particulars";
$HEADER = "Update User Particulars";
include 'header.php';

if ( $_SERVER['REQUEST_METHOD'] == "POST" )
{
	if( !isset($_POST['uid']) || empty($_POST['uid']) )
	{
		echo "You are not logged in.";
	}
	else
	{
		$err = "";

		$db = new PDO("sqlite:/home/john/cloak/data/cloakdb");
		if ( isset($_POST['upduserButton']) && !empty($_POST['upduserButton']) &&
			isset($_POST['fwdaddx']) && !empty($_POST['fwdaddx']) )
		{
			$stmt = $db->prepare( "UPDATE user SET fwdaddr=? WHERE uid=?" );
			if ($stmt->execute( array($_POST['fwdaddx'], $_POST['uid']) ) )
			{
				echo "Updated account.";
			}
			else
			{
				$err .= "<li>There was an error when updating your account. ";
				$err .= "Please contact the administrator.</li>";
			}
		}
		else if ( isset($_POST['updpwdButton']) &&
		!empty($_POST['updpwdButton']) )
		{

			if( !isset($_POST['password']) || empty($_POST['password']) )
			{
				$err .= "<li>You did not enter your old password.</li>";
			}

			if ( !isset($_POST['newpwd']) || empty($_POST['newpwd']) )
			{
				$err .= "<li>You did not enter a new password.</li>";
			}

			if ( !isset($_POST['newpwd2']) || empty($_POST['newpwd2']) )
			{
				$err .= "<li>You did not re-type the new password.</li>";
			}

			if ( strlen($_POST['newpwd']) < 8 )
			{
				$err .= "<li>Your new password is too short. ";
				$err .= "It must be at least 8 characters long.</li>";
			}

			if ( $_POST['newpwd'] != $_POST['newpwd2'] )
			{
				$err .= "<li>New passwords do not match.</li>";
			}

			if ( empty($err) )
			{
				// Check if current password is valid
				$curpwd="{PLAIN-MD5}".md5($_POST['password']);
				$stmt = $db->prepare( "SELECT COUNT(*) as n FROM user WHERE uid=? AND spwd=?" );
				$stmt->execute( array($_POST['uid'], $curpwd) );
				$row = $stmt->fetch();	

	
				if ($row['n'] == 1)
				{
					// Update new password
					$newpwd="{PLAIN-MD5}".md5($_POST['newpwd']);
					$stmt = $db->prepare( 'UPDATE user SET spwd=? WHERE uid=?' );
					if ($stmt->execute( array($newpwd, $_POST['uid']) ))
					{
						echo "Your password has been updated.";
					}
					else
					{
						$err .= "<li>There was an error when updating your password. ";
						$err .= "Please contact the administrator.</li>";
					}
				}
				else
				{
					$err .= "<li>Incorrect old password.</li>";
				}
			}
		}
		else
		{
			$err .= "<li>Unknown option. Please contact the administrator.</li>";
		}

		if (!empty($err))
		{
			echo "<font color=\"red\">";
			echo $err;
			echo "</font>";

			include 'updform.php';
		}
	}

}
else
{
	include 'updform.php';
}
include 'navi.php';
include 'footer.php';
?>

