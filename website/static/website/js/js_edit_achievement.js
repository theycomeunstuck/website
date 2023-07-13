// document.addEventListener("DOMContentLoaded", function() {
//     var showScanLink = document.getElementById("show_scan");
//     if (showScanLink) {
//         showScanLink.addEventListener("click", function(event) {
//             event.preventDefault();
//
//             // Выполнение запроса AJAX для загрузки файла на сервер
//             var xhr = new XMLHttpRequest();
//             xhr.open("POST", "URL_загрузки_файла", true);
//             xhr.onreadystatechange = function() {
//                 if (xhr.readyState === 4) {
//                     if (xhr.status === 200) {
//                         // Успешная загрузка файла
//
//                         // Отправка файла пользователю
//                         var downloadUrl = "URL_скачивания_файла";
//                         var downloadLink = document.createElement("a");
//                         downloadLink.href = downloadUrl;
//                         downloadLink.download = "{{ achievement.competition_name|slugify }}.{{ achievement.file_format }}";
//                         downloadLink.click();
//
//                         // Удаление файла с сервера
//                         var deleteUrl = "URL_удаления_файла";
//                         var deleteRequest = new XMLHttpRequest();
//                         deleteRequest.open("DELETE", deleteUrl, true);
//                         deleteRequest.send();
//                     } else {
//                         // Ошибка загрузки файла
//                         console.error("Ошибка загрузки файла");
//                     }
//                 }
//             };
//             xhr.send(форма_загрузки_файла);
//         });
//     }
// });
