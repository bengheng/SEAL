<?php
session_start();

$TITLE="SEAL - Instructions";
$HEADER="Instructions";
include 'header.php';
?>

<font color="red"><b>Note: Currently, these instructions are customized for users with a
University of Michigan uniqname and email account.</b>
</font><br><br>

You can view SEAL as a 'guard' for your traditional email account. There are two ways in which you can set up SEAL. Click on the appropriate link for your needs.<br><br>

<ol>
<li><a href="simple.php">Simple</a>: User cannot reply to emails.</li>
<li><a href="advance.php">Advance</a>: User can reply to emails using authenticated SMTP.</li>
</ol>

<?php
include 'navi.php';
include 'footer.php';
?>
