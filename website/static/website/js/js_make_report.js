$(document).ready(function () {
    $(".chosen-select").chosen({
        placeholder_text_multiple: "Выберите опции",
        no_results_text: "Ничего не найдено"
    });

    $(".chosen-select").on("change", function () {
        var selectedOptions = $(this).val();
        var selectedValuesDiv = $(".selected-values");
        selectedValuesDiv.empty();

    });

    $(".chosen-container-multi .chosen-choices").on("click", function (e) {
        if ($(e.target).hasClass("search-choice-close")) {
            var unselectedOption = $(e.target).closest(".search-choice");
            var optionValue = unselectedOption.data("option-array-index");
            $(".chosen-select").find('option[value="' + optionValue + '"]').removeAttr("selected");
            $(".chosen-select").trigger("chosen:updated");
        }
    });
});

