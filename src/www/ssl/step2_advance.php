<?php
$TITLE="SEAL - Instructions Step 2 (Advance)";
$HEADER="Instructions - Step 2 (Advance)";
include 'header.php';
?>
<h3><a href="step1_advance.php"><font size=-1>Step 1: Register with SEAL</font></a></h3>
<h3>Step 2: Configure Gmail's "Send As" Feature</h3>
<h3><a href="step3_advance.php"><font size=-1>Step 3: Start using SEAL</font></a></h3>
<hr/><br>
<p><i>[Click on the images to see larger versions.]</i></p><br>
<p>
Set up Gmail to send mail via authenticated SMTP for your SEAL account:
<ol>
<li>Log into your Gmail account.</li>
<li>Go to Mail Settings &gt; Accounts and Import.<br>
<a href="images/step2a.png"><img src="images/step2a.png" alt="step2a.png" width="350"/></a>

</li>
<li>Under "Send mail as", click "Send mail from another address".</li>
<li>A popup titled "Add another email address you own" will appear. Enter
    a name for yourself and your account email address
     (&lt;your 'SEAL' username&gt;@<?php echo $_SERVER['SERVER_NAME']?>). Click "Next Step".<br>
<a href="images/step2b.png"><img src="images/step2b.png" alt="step2b.png" width="250"/></a>

</li>
<li>Select the radio button "Send through <?php echo $_SERVER['SERVER_NAME']; ?> SMTP servers".<br>
<a href="images/step2c.png"><img src="images/step2c.png" alt="step2c.png" width="250"/></a>

</li>
<li>Additional fields will appear. Use the following settings.
	<table border=1>
	<tr>
	<td>SMTP Server: </td>
	<td><?php echo $_SERVER['SERVER_NAME'];?></td>
	<tr>
	<tr>
	<td>Port: </td>
	<td>465</td>
	</tr>
	<tr>
	<td>Username: </td>
	<td>&lt;your 'seal' username&gt;</td>
	</tr>
	<tr>
	<td>Password: </td>
	<td>&lt;your 'seal' password&gt;</td>
	</tr>
	</table>
	Select "Secured connection using TLS" (if TLS does not work, use SSL
instead).
</li>
<li>Click "Add Account »". Gmail will send a verification email, which will
appear in the inbox of this same account. Enter the verification code or follow
the given link. It should now be configured.<br>
<a href="images/step2d.png"><img src="images/step2d.png" alt="step2d.png" align="top" width="180"/></a>
<a href="images/step2e.png"><img src="images/step2e.png" alt="step2e.png" align="top" width="180"/></a>
<br>
</li>
<li>Back in the Accounts and Import page, your 'SEAL' account should now appear under "Send mail as." If desired, select the "Default" button next to the 'SEAL' account so that messages you send will be sent through the SEAL service by default.  Otherwise, you may have to choose to send through the SEAL service each time you compose a new message. You also may want to select the option "Reply from the same address the message was sent to" so that Gmail will automatically arrange for your reply messages to correctly decide whether to use the SEAL service.<br>
<a href="images/step2f.png"><img src="images/step2f.png" alt="step2f.png" width="250"/></a>
</li>
</ol>
</p><br>
<p>
Click <a
href="http://mail.google.com/support/bin/answer.py?answer=22370">here</a> for
more information about Gmail's "Send As" feature.
</p><br>

<?php
include 'navi.php';
include 'footer.php';
?>
