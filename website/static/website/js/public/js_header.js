// profile.js

function confirmLogout() {
    var result = confirm("Вы уверены, что хотите выйти?");

    if (result) {
        // Передача ответа в Django
        // Очистка куки или выполнение других действий

        // Пример перенаправления на страницу выхода в Django
        window.location.href = "/logout"; // Здесь указывается абсолютный путь к URL-шаблону "logout"
    }
}

function redirectProfile() {
    window.location.href = "/profile"
}
