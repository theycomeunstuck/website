//
// function handleButtonClick(buttonName) {
//     const xhr = new XMLHttpRequest();
//     xhr.open('POST', '/profile/buttons/', true);
//     xhr.setRequestHeader('Content-Type', 'application/json');
//     xhr.onreadystatechange = function() {
//         if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
//             const response = JSON.parse(xhr.responseText);
//             if (response.redirect) {
//                 window.location.href = response.redirect;
//             }
//         }
//     };
//     const data = JSON.stringify({ buttonName });
//     xhr.send(data);
// }
