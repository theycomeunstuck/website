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

function handleButtonClick(buttonName) {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/profile/buttons/', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            if (response.redirect) {
                window.location.href = response.redirect;
            }
        }
    };
    const data = JSON.stringify({ buttonName });
    xhr.send(data);
}
