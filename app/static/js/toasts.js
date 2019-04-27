function myAlertTop() {
    $(".myAlert-top").fadeIn();
    setTimeout(function () {
        $(".myAlert-top").fadeOut();
    }, 3500);
}

function myAlertBottom() {
    $(".myAlert-bottom").fadeIn();
    setTimeout(function () {
        $(".myAlert-bottom").fadeOut();
    }, 3500);
}

function myAlertTopSignup() {
    $(".myAlert-top-signup").fadeIn();
    setTimeout(function () {
        $(".myAlert-top-signup").fadeOut();
    }, 12500);
}

myAlertBottom();
myAlertTop();
myAlertTopSignup();