<?php
session_start();

$loggedin = (isset($_SESSION['user']) && !empty($_SESSION['user']) &&
isset($_SESSION['uid']) && !empty($_SESSION['uid']));

$TITLE = "SEAL - Contact";
$HEADER = "Contact";

include 'header.php';
?>

If you encounter any problem using SEAL, please send an email to either of the
administrators at the following email addresses.
<br><br>
<ol>

<SCRIPT TYPE="text/javascript">
<!-- 
// protected email script by Joe Maller
// JavaScripts available at http://www.joemaller.com
// this script is free to use and distribute
// but please credit me and/or link to my site

emailE1=('admin1.3pttzqwf@' + 'seal.eecs.umich.edu')
document.write('<li><A href="mailto:' + emailE1 + '">' + emailE1 + '</a></li>')

emailE2=('admin2.z9a3xah1@' + 'seal.eecs.umich.edu')
document.write('<li><A href="mailto:' + emailE2 + '">' + emailE2 + '</a></li><br>')
 //-->
</script>

<NOSCRIPT>
    <em>Email address protected by JavaScript.<BR>
    Please enable JavaScript to contact us.</em>
</NOSCRIPT>

</ol>

<?php
include 'navi.php';
include 'footer.php';

?>
