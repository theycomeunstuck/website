
function confirmLogout() {
    var result = confirm("Вы уверены, что хотите выйти?");

    if (result) {
        window.location.href = "/logout";
    }
}

function redirectProfile() {
    window.location.href = "/profile"
}
