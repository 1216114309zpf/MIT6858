<?php
do {
    $to = filter_var($_REQUEST['to'], FILTER_SANITIZE_EMAIL);
    //$to = "19930127zpf@sjtu.edu.cn";

    $payload = $_REQUEST['payload'];


    $from = $to;
    $subject = "Message from $from";
    $message = "Payload:$payload";
    if (!mail($to, $subject, $message)) {
        header("HTTP/1.0 503 Service Unavailable");
        echo "Failed to relay e-mail to e-mail server";
        return;
    }

    echo "Sent!";
    return;
} while(0);
?>

