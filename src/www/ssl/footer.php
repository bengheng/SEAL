</div>
<div id="clear"></div>
</div>
<div id="bottom"></div>
</div>

<div id="footer">
<font size="-1" color="#666666">&copy;2011 - University of Michigan

<?php
$loggedin = (isset($_SESSION['user']) && !empty($_SESSION['user']) &&
isset($_SESSION['uid']) && !empty($_SESSION['uid']));
if ($loggedin)
{
	//<a href="cloak.f5y6qbtu@cloak.dyndns-mail.com">cloak.f5y6qbtu@cloak.dyndns-mail.com</a><br>
	//<img src="/images/contact.png" width="13%"/>
}
?>

&middot; <a href="privacy.php">Privacy Policy</a><br>
Design by <a href="http://www.minimalistic-design.net">Minimalistic Design</a>
</font>
</div>

</body>
</html>
