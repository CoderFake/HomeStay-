function loadOverlay() {
    $('#LoadOverlay').fadeIn();
}

function closeOverlay() {
    setTimeout(function () {
        $('#LoadOverlay').fadeOut();
    }, 500);
}