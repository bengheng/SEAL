<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title><?php echo $TITLE;?></title>
<meta http-equiv="Content-Language" content="English" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<link rel="stylesheet" type="text/css" href="/style.css" media="screen" />
</head>
<body>
<div id="wrap">

<div id="top"></div>

<div id="content">

<div class="header">
<h1><a href="/index.php">SEAL</a></h1>
<h2><?php echo $HEADER;?></h2>
</div>

<div class="breadcrumbs">
<?php
$loggedin = (isset($_SESSION['user']) && !empty($_SESSION['user']) &&
isset($_SESSION['uid']) && !empty($_SESSION['uid']));
if ($loggedin)
{
?>
	<span>
	<a href="/index.php">Home</a> &middot;
	<a href="member.php">My Alias Names</a> &middot;
	<a href="logout.php">Logout</a>
	</span>
<?php
}
else {
?>
	<a href="/index.php">Home</a> &middot;
	<a href="/register.php">Register</a>
<?php
}
?>

<span style="float: right; padding-right: 5px">
<?php
if ($loggedin)
{
?>
	Logged in as <b><?php echo $_SESSION['user']; ?></b>
<?php
} else
{
?>
	Not logged in
<?php
}
?>
</span>
</div>

<div class="middle">

