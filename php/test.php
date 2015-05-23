<?php
$output = shell_exec('../shell/getJson.sh 2>&1');
echo "<pre>$output</pre>";
?>
