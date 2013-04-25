<?php
session_start();

$TITLE = "SEAL - Login";
$HEADER = "Login";
include 'header.php';

if($_SERVER["REQUEST_METHOD"] == "POST")
{
	// Ref: www.devarticles.com/c/a/PHP/PHP-for-Beginners-by-a-Beginners/1/

	if (!isset($_POST['username']) || !isset($_POST['password'])) {
		// Page accessed directly. Redirect back to the login form if necessary.
		header("Location:index.html");
	} elseif (empty($_POST['username']) || empty($_POST['password'])) {
		// Form fields are empty. Redirect back to the login page if they are.
		header("Location:index.html");
	} else {
		// Convert field values to simple variables.

		// Add slashes to the username and md5() the password.
		$user = addslashes($_POST['username']);
		$pass = md5($_POST['password']);
		try {
			$db = new PDO("sqlite:/home/john/cloak/data/cloakdb");
			$result = $db->query("SELECT * FROM user WHERE username='$user'");
			$row = $result->fetch();
			$err = 0;
			if (!$row) {
				$err = 1;
			} 
			else {
				$dbpass1 = $row["spwd"];
				// Password must be prefixed by {PLAIN-MD5}
				$prefix = "{PLAIN-MD5}";
				$pos = stripos($dbpass1, $prefix);
				if ($pos !== false) {
					// Has prefix
					$dbpass2 = substr($dbpass1, strlen($prefix));
					if ($dbpass2 == $pass) {
						$_SESSION['user'] = $user;
						$_SESSION['uid'] = $row['uid'];
						header("Location:member.php");
					}
					else {
						$err = 1;
					}
				}
			}

			if ($err == 1) {
				echo "Incorrect username/password.<br>";
			}


		} catch (Exception $e) {
			echo $e->getMessage();
		}
	}
}
include 'navi.php';
include 'footer.php';
?>
