function checkFileSize(input) {
    if (input.files && input.files[0]) {
        var fileSize = input.files[0].size; // Размер файла в байтах
        var maxSize = 2 * 1024 * 1024; // 2 МБ в байтах

        if (fileSize > maxSize) {
            alert('Размер файла слишком большой! Максимальный размер файла - 2 МБ.');
            input.value = '';
        }
    }
}
