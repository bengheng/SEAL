<?php
$TITLE = "Semi-private Email ALiases";
$HEADER = "Semi-private Email ALiases";

session_start();

if (isset($_SESSION['user']) && !empty($_SESSION['user']) &&
	isset($_SESSION['uid']) && !empty($_SESSION['uid']))
{
	include 'header.php';
	//echo "Welcome, ".$_SESSION['user']."!";
	include 'intro.php';
}
else
{
	include 'header.php';
	echo "<form method=\"POST\" action=\"login.php\">";
	echo "<table>";
	echo "<tr>";
	echo "<td>Username: </td>";
	echo "<td><input type=\"text\" name=\"username\"></td>";
	echo "</tr>";
	echo "<tr>";
	echo "<td>Password: </td>";
	echo "<td><input type=\"password\" name=\"password\"></td>";
	echo "</tr>";
	echo "<tr>";
	echo "<td><input type=\"submit\" value=\"Login\" name=\"login\"></td>";
	echo "</tr>";
	echo "</table>";
	echo "</form><br>";
	include 'intro.php';
}

include 'navi.php';
include 'footer.php';

?>
