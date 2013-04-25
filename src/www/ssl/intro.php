<h2>What is SEAL?</h2>


<p>Traditionally, users expect their email addresses to be long-lasting. Many
will take steps to prevent their email addresses from being <i>leaked</i>,
including creating multiple email addresses and distributing each address only
to a certain group of contacts, in the hope that these addresses will never
fall into the hands of spammers. However, we all know that once we distribute an
address, we no longer have any control on who might send us spam on it.
Sometimes, users incorrectly believe that their contacts will never spam them.
Unfortunately, when that happens, the best bet is to go yet again through the whole
process of creating another email address. Other times, spammers can just
guess the users' email addresses via a dictionary attack.</p><br>

<?php
/*
<object data="images/lifecycle.svg" type="image/svg+xml"
width=100%></object>
*/
?>
<image src="images/lifecycle.png" width=100% /><br><br>

<p><b>SEAL</b>, short for Semi-private Email ALiases, introduces the concept of
an email alias lifecycle. A SEAL alias always starts off as <i>unrestricted</i>.
Anybody can send emails to an unrestricted alias until the user observes that it
has been leaked. The user can then mark the alias as <i>partly restricted</i>. A
new unrestricted alias is automatically generated. Contacts will be
notified of the new alias if they send emails to the partly restricted alias. At
this stage, unknown senders will be challenged with a CAPTCHA and permission is
sought from the user before mails from these senders are relayed to the user's
inbox.</p><br>

<p>When the user decides not to allow any more new senders to use the alias,
they can mark the alias as <i>fully restricted</i>. Now, no CAPTCHA will be
issued to unknown senders and email from them will never be relayed to the
user's inbox. However, known senders can continue sending emails to the
alias. In the last stage, the user can <i>disable</i> an alias, so that it 
is discarded.</p>

