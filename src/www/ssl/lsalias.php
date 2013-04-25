<p>This is a list of the alias names that you control. To view the aliases that
that have been 
generated for an alias name, simply click on it.</p><br>

<?php
session_start();

$uid = $_SESSION['uid'];

$db = new PDO("sqlite:/home/john/cloak/data/cloakdb");

if(isset($_POST['setpri'])) {
	$aliasname = $_POST['id'];
	$db->query("UPDATE alias SET isprimary=0 WHERE uid='$uid' AND isprimary=1");
	$db->query("UPDATE alias SET isprimary=1 WHERE uid='$uid' AND aliasname='$aliasname'");
}

if(isset($_POST['unsetpri'])) {
	$aliasname = $_POST['id'];
	$db->query("UPDATE alias SET isprimary=0 WHERE uid='$uid' AND aliasname='$aliasname'");
}

$result = $db->query("SELECT aliasname, isprimary FROM alias WHERE uid='$uid'"); //AND isprimary=1");

$primary = array();
$notprimary = array();

foreach( $result as $row) {
$raliasname = $row['aliasname'];

if($row['isprimary'])
	$primary[] = $raliasname;

else
	$notprimary[] = $raliasname;
}

//if(count($primary) == 0)
//{
/*?>
<p>Select a primary alias by click on the "Set Primary"
button. Only <i>one</i> alias name can be set as primary at any one time.
A primary alias is used in-conjunction with the Firefox extension when
an alias is not specified. If no primary alias is set and no alias is
specifed, the extension fails.
Click <a href="doc/moniker_03.xpi">here</a> for the latest
copy of the extension.</p><br>
<?php  */
//}

try {
	if(count($primary) > 0)
	{
		$i = 0;

?>
<table><thead><tr><td colspan="3"><b>Primary Alias Name</b> <span style="font-style:italic;
font-size:xx-small"><a id="primToggle" href="javascript:toggleDisplay('prim');">What is a primary alias
name?</a></span></td></tr></thead><tbody>
<?php

		foreach($primary as $cur_aliasname) {
			$i = $i + 1;
	
			echo "<tr>\n";
			echo "<td valign=\"center\">".strval($i)."</td>\n";
			echo "<td valign=\"center\">";
			echo "<form id=\"".$cur_aliasname."Form\" action=\"lsaliasname.php\" method=\"post\">";
			echo "<input type=\"hidden\" name=\"aliasname\" value=\"".$cur_aliasname."\">";
			echo "</form>";
			echo "<a href='javascript:document.getElementById(\"".$cur_aliasname."Form\").submit();'>".$cur_aliasname."</a>";
			echo "</td>\n";

			echo "<td valign=\"center\">\n";
			echo "<form method=\"POST\" action=\"".$_SERVER['PHP_SELF']."\">\n";
			echo "<input type=\"hidden\" name=\"id\" value=\"".$cur_aliasname."\" />\n";
	
			echo "<input type=\"submit\" name=\"unsetpri\" value=\"Unset As Primary\" />\n";
	
			echo "</form>\n";
			echo "</td>\n";
			echo "</tr>\n";
		}

		echo "</tbody>";
		//echo "<tfoot><tr><td colspan=\"3\"><br>You have ".$i." <i>primary</i> alias names.<br></td></tr></tfoot>";
		echo "</table><br>";
	}

	else
	{
?>
No <i>primary alias name</i> has been set.&nbsp;&nbsp;<span style="font-style:italic;
font-size:xx-small"><a id="primToggle" href="javascript:toggleDisplay('prim');">What is a primary alias
name?</a></span>
<br><br>
<?php
	}
?>
<script language="javascript">
var toggleTextValue = new Array();
function toggleDisplay(elemName) {
	if (document.getElementById) {
		var elemExplain = document.getElementById(elemName + "Explain");
		var toggleText  = document.getElementById(elemName + "Toggle");
	}
	else if (document.layers) {
		var elemExplain = document.elemExplain;
		var toggleText  = document.toggleText;
	}

	if (elemExplain.style.display == 'none') {
		toggleTextValue[elemName] = toggleText.innerHTML;
		toggleText.innerHTML = 'Hide this explanation!';
		elemExplain.style.display = 'block';
	}
	else {
		toggleText.innerHTML = toggleTextValue[elemName];
		elemExplain.style.display = 'none';
	}
}
</script>
<div id="primExplain" style="display: none">
<div style="border: 1px solid blue; padding: 10px;
background-color: #EFEFFF;">
A <b>primary alias name</b> is used in conjunction with the SEAL Firefox extension when
an alias name is not specified. If no primary alias name is set and no alias
name is specifed, the extension fails.
<br><br>
Click <a href="doc/moniker_03.xpi">here</a> for the latest
copy of the SEAL Firefox extension.
<br><br>
You can set an alias name as the primary by clicking on the "Set As Primary"
button next to it. Only <i>one</i> alias name can be set as the primary at any
one time.
</div>
<br>
</div>

<?php

	$j = 0;

	echo "<table><thead><tr><td colspan=\"3\"><b>Non-Primary Alias Names</b> (".count($notprimary).")</td></tr></thead><tbody>";

	foreach($notprimary as $cur_aliasname) {
		$j = $j + 1;

		echo "<tr>\n";
		echo "<td valign=\"center\">".strval($j)."</td>\n";
		echo "<td valign=\"center\">";
		echo "<form id=\"".$cur_aliasname."Form\" action=\"lsaliasname.php\" method=\"post\">";
		echo "<input type=\"hidden\" name=\"aliasname\" value=\"".$cur_aliasname."\">";
		echo "</form>";
		echo "<a href='javascript:document.getElementById(\"".$cur_aliasname."Form\").submit();'>".$cur_aliasname."</a>";
		echo "</td>\n";

		echo "<td valign=\"center\">\n";
		echo "<form method=\"POST\" action=\"".$_SERVER['PHP_SELF']."\">\n";
		echo "<input type=\"hidden\" name=\"id\" value=\"".$cur_aliasname."\" />\n";

		echo "<input type=\"submit\" name=\"setpri\" value=\"Set As Primary\" />\n";

		echo "</form>\n";
		echo "</td>\n";

		echo "</tr>\n";
	}

	echo "</tbody>";
	//echo "<tfoot><tr><td colspan=\"3\"><br>You have ".$j." <i>non-primary</i> alias names.<br></td></tr></tfoot>";
	echo "</table>";

	if(count($notprimary) + count($primary) == 0)
	{
?>
You have no aliases at this time.  You can get one <a
href="getalias.php">here</a>.
<?php
	}

} catch (Exception $e) {
	echo $e->getMessage();
}

?>

