<?php
$postcode = $_GET['postcode'];
exec("python api.py $postcode", $output, $ret_code);
//json_decode($output);
print_r(implode("\n",$output));
?>
