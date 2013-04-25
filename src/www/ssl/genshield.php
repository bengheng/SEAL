<?php
$TITLE = "SEAL - Shield";
$HEADER = "Get My Shield!";
include 'header.php';
?>

<font color="red"><b>Warning: This is an experimental feature!</b></font><br>

<p>
To generate your email shield, follow these steps:
<ol>
<li> (optional) Enter alias and hint. If no alias is entered, a primary alias will be chosen.</li>
<li> Click "Generate".</li>
<li> Create a php file shield.php with the generated php code.</li>
<li> Download <a href="doc/aes.tar.gz">aes.tar.gz</a>. It contains two required scriptrs, aes.class.php and aesctr.class.php. Untar the files into the same folder as shield.php.
<li> Use the email variable in places where you want your email to be shielded. For an example, right click this <a href="testshield.php">link</a>, select "Save Link As..." and open the downloaded file with your favorite editor.</li>
</ol>
</p>

<form method="POST" action="<?php echo $_SERVER['PHP_SELF']; ?>">


<table>

	<tr>
		<td>Alias :</td>
		<td><input type="text" name="alias"></td>
	</tr>
	<tr>
		<td>Hint :</td>
		<td><input type="text" name="hint"></td>
	</tr>
	<tr>
		<td><input type="submit" value="Generate" name="generate"></td>
	</tr>
	<tr>
		<td colspan="2">
		<textarea rows="45" cols = "70">
<?php
		if(isset($_POST['generate']))
		{
		session_start();

		$uid = $_SESSION['uid'];
		$user = $_SESSION['user'];
		$alias = $_POST['alias'];
		$hint = $_POST['hint'];

		// Connects to the database, generates a web session key
		try {
			$db = new PDO("sqlite:/home/john/cloak/data/cloakdb");

			// Generate key
			$n = base64_encode( strval(rand()) );

			// add to database
			$db->query( "INSERT INTO websession (uid, sessionkey) VALUES('$uid', '$n')" );
			$wid = $db->lastInsertId();
		} catch (Exception $e) {
			echo $e->getMessage();
		}

		echo "<?php\n";
		echo "require 'aes.class.php';\n";
		echo "require 'aesctr.class.php';\n";
		echo "function get_ip_address() {\n";
		echo "  foreach (array('HTTP_CLIENT_IP', 'HTTP_X_FORWARDED_FOR', 'HTTP_X_FORWARDED', 'HTTP_X_CLUSTER_CLIENT_IP', 'HTTP_FORWARDED_FOR', 'HTTP_FORWARDED', 'REMOTE_ADDR') as \$key) {\n";
		echo "    if (array_key_exists(\$key, \$_SERVER) === true) {\n";
		echo "      foreach (explode(',', \$_SERVER[\$key]) as \$ip) {\n";
		echo "        if (filter_var(\$ip, FILTER_VALIDATE_IP) !== false) {\n";
		echo "          return \$ip;\n";
		echo "        }\n";
		echo "      }\n";
		echo "    }\n";
		echo "  }\n";
		echo "}\n";
		echo "\$sk = \"$n\";\n";
		echo "\$dat = array(\n";
		echo "    \"user\" => \"$user\",\n";
		echo "    \"domain\" => get_ip_address(),\n";
		echo "    \"alias\" => \"$alias\",\n";
		echo "    \"hint\" => \"$hint\"\n";
		echo ");\n";
		echo "\$req = array(\n";
		echo "    \"user\" => \"$user\",\n";
		echo "    \"w\" => \"$wid\",\n";
		echo "    \"c\" => AesCtr::encrypt( json_encode(\$dat), \$sk, 256)\n";
		echo ");\n";
		echo "\$r = new HttpRequest('https://".$_SERVER['SERVER_NAME']."/cgi-bin/getalias.py?r='.base64_encode( json_encode(\$req) ), HttpRequest::METH_GET);\n";
		echo "  \$r->setContentType = 'Content-Type: text/html';\n";
		echo "  try {\n";
		echo "      \$r->send();\n";
		echo "      if (\$r->getResponseCode() == 200) {\n";
		echo "          \$email = \$r->getResponseBody();\n";
		echo "      }\n";
		echo "      else {\n";
		echo "          echo \"Error \".\$r->getResponseCode();\n";
		echo "      }\n";
		echo "  } catch (HttpException \$ex) {\n";
		echo "      echo \$ex;\n";
		echo "  }\n";
		echo "?>\n";

		}
?>
		</textarea>
		</td>
	</tr>
</table>


</form>

<?php
include 'footer.php';
?>
