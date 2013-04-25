
<?php
session_start();

$TITLE = "SEAL - Get an Alias";
$HEADER = "Get an Alias";
include 'header.php';


function create_alias($db, $uid, $aliasname) {
	// Insert alias into database
	$stmt = $db->prepare( "INSERT INTO alias (uid, aliasname) VALUES(?, ?)" );
	$stmt->execute(array($uid, $aliasname));
	$aid = $db->lastInsertId('aid');

	echo "You now have ownership of this alias name: <i>".$aliasname."</i><br>";
	return $aid;
}

function get_fwdaddx($db, $uid)
{
	$fwdaddr = '';

	try {
		$stmt = $db->prepare( "SELECT fwdaddr FROM user WHERE uid=?" );
		$stmt->execute( array($uid) );
		$result = $stmt->fetch();
		$fwdaddr = $result['fwdaddr'];
	} catch(Exception $e) {
		echo $e->getMessage();
	}

	return $fwdaddr;
}

function create_aliasrnd($db, $uid, $aid, $aliasname) {
	// Execute scriptlet to get rint and rstr
	$cmd = "../webscripts/scriptlet.py";
	$out = `$cmd`;
	$outarr = explode(',', $out);
	$rfloat = (float)$outarr[0];
	$rstr = $outarr[1];

	try {
		$stmt = $db->prepare( "INSERT INTO aliasrnd (uid, aid, aliasname, aliasrand) VALUES (:uid, :aid, :aliasname, :rint);" );
		$stmt->bindParam(':uid', $uid);
		$stmt->bindParam(':aid', $aid);
		$stmt->bindParam(':aliasname', $aliasname);
		$stmt->bindParam(':rint', $rfloat);
		$stmt->execute();
	} catch(Exception $e) {
		echo $e->getMessage();
	}

	/*
	$cmd = "./../webscripts/makealias.py ".$uid." ".$aliasname."";
	$aliasres = `$cmd`;

	if($aliasres == "" || strpos($aliasres,"Error:") !== FALSE)
	{
		echo "There was an unexpected error while creating your alias<br>";
		//echo $aliasname;
		echo $cmd."<br>";
		echo $aliasres;
		return;
	}

	$aliaspair = explode('.', $aliasres, 2);
	*/

	echo "You can distribute any of the following SEAL aliases to your contacts.<br><br>";
	echo "<p align=\"center\"><b>";

	/*
	if(count($aliaspair) < 2)
	{
		echo $aliasres."@".$_SERVER['SERVER_NAME'];
	}
	else
	{
		$aliaspair = array_map('trim', $aliaspair);
		//$aliaspair[1] = trim($aliaspair[1]);

		echo $aliaspair[0].".".$aliaspair[1]."@".$_SERVER['SERVER_NAME'];
		echo "<br>";
		echo $aliaspair[0]."_".$aliaspair[1]."@".$_SERVER['SERVER_NAME'];
		echo "<br>";
		echo $aliaspair[0]."-".$aliaspair[1]."@".$_SERVER['SERVER_NAME'];
	}
	*/

	echo $aliasname.".".$rstr."@".$_SERVER['SERVER_NAME']."<br>";
	echo $aliasname."_".$rstr."@".$_SERVER['SERVER_NAME']."<br>";
	echo $aliasname."-".$rstr."@".$_SERVER['SERVER_NAME'];
	echo "</b></p>";
	$fwdaddx = get_fwdaddx($db, $uid);
	echo "<br>Email sent to these aliases will be relayed to your forwarding
		email address, <b>".$fwdaddx."</b>. Note that the only difference
		amongst them is the separator used, which could be a period '.', an
		underscore '_', or a dash '-'.";

	// Send an email with the same contents so that the user has
	// the record in her inbox.
	$cmd = '../webscripts/getalias.py '.$fwdaddx.' '.$aliasname.' '.$rstr;
	echo `$cmd`;
}

if ( !$dontshow )
{
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
Each <i>alias</i> is prefixed by an <i>alias name</i> followed by a string of
random characters. There can be multiple aliases created from a single <i>alias
name</i>. For example, one can own an alias name called <i>sch</i> and
generate the aliases such as "sch.ua5pkb6q", "sch.9dc1dwst", and so on.
The user can then use "sch.ua5pkb6q@seal.eecs.umich.edu" for signing up with
<a href="https://piazza.com/">Piazza</a>, and
"sch.9dc1dwst@seal.eecs.umich.edu" for signing up with <a
href="https://bubbl.us/">bubbl.us</a>.
<br><br>
To request for an <i>alias name</i>, enter the desired alias name below and
click 'Get Alias!'. If the alias name is not currently owned or is already owned
by you, an <i>alias</i> based on the alias name will then be randomly generated.
&nbsp;&nbsp;<span style="font-style:italic;
font-size:xx-small"><a id="aliasToggle"
href="javascript:toggleDisplay('alias');">What is an alias?</a></span><br><br>
<div id="aliasExplain" style="display: none">
<div style="border: 1px solid blue; padding: 10px;
background-color: #EFEFFF;">
A <b>SEAL alias</b> is an email address of the form
<div align="center" style="margin-top: 4px; margin-bottom: 4px; font-style: italic;">&lt;alias name&gt;.&lt;random
stuff&gt;@seal.eecs.umich.edu</div>
where <i>&lt;alias name&gt;</i> is the value given below.  You are free to
choose the alias name, but the random part is created by SEAL.  The resulting
email address can be given to anyone (including Piazza) and you will receive
emails addressed to it at your forwarding email address (which can be viewed and
modified in <a href="update.php">Account Settings</a>). You can view all of the
aliases you have already created on the <a href="member.php">My Aliases</a>
page.<br>
</div>
<br>
</div>

<script type="text/javascript">
function isAlphanumeric(str)
{
	var regExp = /^[A-Za-z0-9]$/;
	if (str != null && str != "")
	{
		for (var i = 0; i < str.length; i++)
		{
			if (!str.charAt(i).match(regExp))
			{
				return false;
			}
		}
	}
	else
	{
		return false;
	}
	return true;
}

function validateAlias()
{
	var x=document.forms["getaliasForm"]["aliasname"].value;
	if (x.length > 225) {
		alert( "Alias name is too long. Max length is 225 characters." );
		return false;
	}
	else if (isAlphanumeric(x) == false) {
		alert( "Alias name contains invalid characters. Only alphabets and digits are allowed." );
		return false;
	}
}
</script>

	
<form name="getaliasForm" action="<?php echo $_SERVER['PHP_SELF']; ?>"
onsubmit="return validateAlias();" method="post">
<table>
<tr>
<td>
Alias Name: 
</td>
<td>
<input type="text" name="aliasname" size="20" value="">
</td>
<td>
<input type="submit" value="Get Alias!">
</td>
</tr>
</table>
</form>

<?php

	//$MAXALIASNAMELEN = 254 - strlen($_SERVER['SERVER_NAME']) - 10;
	echo "<div style=\"margin: 10px;\">Note: The maximum length of an alias name is 225 characters.
	Alias names are case-insensitive, and only letters and digits are allowed.</div>";

	if ($_SERVER['REQUEST_METHOD'] == "POST" &&
	isset($_SESSION['uid']) && isset($_POST['aliasname'])) {
		$uid = $_SESSION['uid'];

		$aliasname = $_POST['aliasname'];

		// First, check if aliasname is already owned.
		$db = new PDO("sqlite:/home/john/cloak/data/cloakdb");
		$qstr = "SELECT aid, uid FROM alias WHERE aliasname=\"".$aliasname."\"";
		$result = $db->query($qstr);
		$row = $result->fetch();
		if( !$row ) {
			echo "<div style=\"border: 1px solid green; padding: 10px; background-color: #EFFFEF;\">";
			$aid = create_alias($db, $uid, $aliasname);
			//echo "You now have ownership of this alias name: <i>".$aliasname."</i><br>";
			create_aliasrnd($db,  $uid, $aid, $aliasname);
		}
		else {
			if ( $row['uid'] == $uid) {
				echo "<div style=\"border: 1px solid green; padding: 10px; background-color: #EFFFEF;\">";
				echo "You already own the alias name \"".$aliasname."\".<br>";
				create_aliasrnd($db, $uid, $row['aid'], $aliasname);
			}
			else {
				echo "<div style=\"border: 1px solid red; padding: 10px; background-color: #FFEFEF;\">";
				echo "The alias name \"<i>".$aliasname."</i>\" is unavailable. Please try another alias name.";
			}
		}

		echo "</div>";
	}
}

include 'navi.php';
include 'footer.php';
?>
