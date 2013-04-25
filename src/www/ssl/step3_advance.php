<?php
$TITLE="SEAL - Instructions Step 3 (Advance)";
$HEADER="Instructions - Step 3 (Advance)";
include 'header.php';
?>

<h3><a href="step1_advance.php"><font size=-1>Step 1: Register with SEAL</font></a></h3>
<h3><a href="step2_advance.php"><font size=-1>Step2: Configure Gmail's "Send As" Feature</font></a></h3>
<h3>Step 3: Start using SEAL</h3>
<hr/><br>

<p>To start using SEAL, you need to create aliases for distribution to your
contacts.</p><br>

<h4>Creating an Alias (without sending any messages)</h4>
<p>
Once the above steps have been completed, you can create unrestricted
semi-private aliases for distribution to your contacts.
<ol>
<li>Compose a new message addressed to 'getalias@<?php echo $_SERVER['SERVER_NAME']; ?>' with the 'From:'
    field set to use your 'SEAL' account.</li>
<li>In the 'Subject:' field, enter your desired alias name (i.e., if you want an alias of
    the form 'example.&lt;random&gt;@<?php echo $_SERVER['SERVER_NAME'];?>', then just type 'example').</li>
<li>Send the message.  Any content in the message body will be ignored.</li>
<li>You should receive a response message addressed from 'getalias@<?php echo $_SERVER['SERVER_NAME']; ?>'
    telling you your new alias address. You can now use this alias address to send and receive messages.</li>
</ol>
</p><br>

<h4>Sending a Message using a Not-Yet-Created Alias</h4>
<p>
<ol>
<li>Compose a new message with the 'From:' field set to use your 'SEAL' account.</li>
<li>Compose the message as you would normally.</li>
<li>In the message's 'To:' field, add an entry of the form &lt;aliasname&gt;@<?php echo $_SERVER['SERVER_NAME']; ?>,
    where &lt;aliasname&gt; is the desired alias name for the new alias you wish to send as.
<li>Send the message.</li>
<li>You will receive a reply from the service informing you of the full alias address
    that the message was sent under.</li>
</ol>
</p><br>

<h4>Sending an Email Using a Pre-existing Alias</h4>
<p>
<ol>
<li>Compose a new message with the 'From:' field set to use your 'SEAL' account.</li>
<li>Compose the message as you would normally.</li>
<li>
<ul><br>
	<li>If the alias you wish to use is the only one you have ever used to communicate
    with your recipients, you can then send the message as you would normally and
    the correct alias should be automatically applied.</li>
	<li>Otherwise, add the alias address you wish to use as an additional recipient in
    the 'To:' field (do not put it in the Cc or Bcc fields) and send the message.</li>
</ul>
</li>
</ol>
</p><br>

<?php
include 'navi.php';
include 'footer.php';
?>
