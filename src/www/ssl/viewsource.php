<html>

<head>
<link rel="stylesheet" href="source.css" type="text/css"> 
</head>

<?php
 //$url = "https://".$_SERVER[ 'HTTP_HOST' ].urldecode( $_GET[ "u" ] );
 $lines = file(substr($_GET["u"], 1));

 foreach( $lines as $line_num => $line ) {
  $line = htmlspecialchars( $line );
  $line = str_replace( "&lt;", '<span>&lt;', $line );
  $line = str_replace( "&gt;", '&gt;</span>', $line );
  $line = str_replace( "&lt;!–", '<em>&lt;!–', $line );
  $line = str_replace( "–&gt;", '–&gt;</em>', $line );

  echo "<span class=\"linenumber\">Line <strong>$line_num </strong></span> : " . $line . "<br/>\n";
 }

?>

</html>
