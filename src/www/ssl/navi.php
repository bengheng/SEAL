</div>
		
<div class="right">

<?php
$loggedin = (isset($_SESSION['user']) && !empty($_SESSION['user']) &&
isset($_SESSION['uid']) && !empty($_SESSION['uid']));

if ($loggedin)
{
	if (!$db)
	{
		$db = new PDO("sqlite:/home/john/cloak/data/cloakdb");
	}

	$uid = $_SESSION['uid'];

	$stmt = $db->prepare( "SELECT COUNT(*) AS cnt FROM alias WHERE uid=?" );
	$stmt->execute( array($uid) );
	$row = $stmt->fetch();
	if ($row['cnt'] == 0)
	{
?>
<h2>Reminder</h2>
<font color="red"><b>
You have not created any SEAL aliases. </b></font>
<font color=#3B6EBF>To protect your personal email address, <a
href="getalias.php">create a SEAL alias</a> and distribute that to your contacts.
</font>
<?php
}
?>

<h2>Navigation</h2>

<ul>
<li><a href="member.php">My Alias Names</a></li>
<li><a href="getalias.php">Get Alias</a></li>
<li><a href="lsaliasname.php">Show Alias Restrictions</a></li>
<li><a href="genshield.php">Get My Shield!</a></li>
<li><a href="update.php">Account Settings</li>
<li><a href="logout.php">Logout</a></li>
<li><a href="instructions.php">Instructions</a></li>
<li><a href="contact.php">Contact</a></li>

</ul>

<?php
}
else
{
?>

<h2>Navigation</h2>

<ul>
<li><a href="register.php">Register</a></li>
<li><a href="instructions.php">Instructions</a></li>
<li><a href="reminder.php">Reset Password</a></li>
<li><a href="http://www.eecs.umich.edu">EECS</a></li>
<li><a href="contact.php">Contact</a></li>
</ul>
<?php
}
?>
