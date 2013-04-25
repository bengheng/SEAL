<?php
session_start();

$TITLE = "SEAL - List of Aliases Restrictions";
$HEADER = "List of Alias Restrictions";
include 'header.php';

$uid = $_SESSION['uid'];

echo "<font color=\"red\"><b>[Experimental]</b></font>";

if(isset($_SESSION['uid']) && isset($_POST['aliasname'])) {
	$aliasname = $_POST['aliasname'];
	echo "<p>This is a list of aliases generated for the aliasname <b>".$aliasname."</b>.</p><br>";
}
else {
	echo "<p>This is a list of aliases generated for <b>all</b> aliasname.</p><br>";
}

echo "<p>If an alias is <i>unrestricted</i>, you can receive emails from all
senders on it. If an alias is <i>partly-restricted</i>, you can only receive
emails from senders not marked as untrusted.</p><br><p>We only show alias
variants using the period character '.', which is interchangeable with an
underscore '_' or a dash '-'.</p><br>";
echo "<table border=1>";

$db = new PDO("sqlite:/home/john/cloak/data/cloakdb");

if(isset($_POST['set_partly_restricted'])) {
	$rid = $_POST['rid'];
	$db->query("UPDATE aliasrnd SET istrusted=0, truststamp=0 WHERE rid='$rid'");
}

if(isset($_POST['unset_partly_restricted'])) {
	$rid = $_POST['rid'];
	$db->query("UPDATE aliasrnd SET istrusted=CURRENT_TIMESTAMP WHERE rid='$rid'");
}

try {
	if (isset($_POST['aliasname'])) {
		$qstr = "SELECT rid, aliasrand, istrusted FROM aliasrnd WHERE uid='$uid' AND aliasname LIKE \"$aliasname\"";
	}
	else {
		$qstr = "SELECT rid, aliasname, aliasrand, istrusted FROM aliasrnd WHERE uid='$uid'";
	}
	$result = $db->query( $qstr );

	$i = 1;
	echo "<tr><td>#</td><td>Aliasname</td><td>Status</td><td>Update</td></tr>";
	foreach( $result as $row) {
		$rid = $row['rid'];

		// Convert to rstr
		$aliasrand = $row['aliasrand'];
		$cmd = "../webscripts/scriptlet.py ".$aliasrand;
		$out = `$cmd`;
		$outarr = explode(',', $out);
		$aliasrand = $outarr[1];
		$istrusted = $row['istrusted'];

		if (!isset($_POST['aliasname'])) {
			$aliasname = $row['aliasname'];
		}

		echo "<tr>\n";
		echo "<td valign=\"center\">".strval($i)."</td>\n";
		echo "<td valign=\"center\">".$aliasname.".".$aliasrand."@".$_SERVER['SERVER_NAME']."</td>\n";

		if ($istrusted == 1)
		{
			echo "<td>Unrestricted</td>";
		}
		else
		{
			echo "<td>Partly Restricted</td>";
		}

		echo "<td valign=\"center\">\n";
		echo "<form method=\"POST\" action=\"".$_SERVER['PHP_SELF']."\">\n";
		echo "<input type=\"hidden\" name=\"rid\" value=\"".$rid."\" />\n";
		echo "<input type=\"hidden\" name=\"aliasname\" value=\"".$aliasname."\" />\n";

		if ($istrusted != 1) {
			echo "<input type=\"submit\" name=\"unset_partly_restricted\" value=\"Unset Partly-Restricted\" />\n";
		}
		else {
			echo "<input type=\"submit\" name=\"set_partly_restricted\" value=\"Set Partly-Restricted\" />\n";
		}
		echo "</form>\n";
		echo "</td>\n";

		echo "</tr>\n";
		$i = $i + 1;
	}
} catch (Exception $e) {
	echo $e->getMessage();
}

echo "</table>";
//include 'navi.php';
include 'footer.php';
?>
