<html lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Email Shield Example</title>
</head>
<body>

<p>My email is <?php require 'shield.php'; echo $email ?>.</p>

<form method="GET" action="viewsource.php" >
<input type="hidden" name="u" value=<?php echo $_SERVER['PHP_SELF'] ?> />
<input type="submit" value="View Source" />
</form>
</body>
</html>
