document.addEventListener("DOMContentLoaded", function() {
  var showScanLink = document.getElementById("show_scan");
  if (showScanLink) {
    showScanLink.addEventListener("click", function(event) {
      event.preventDefault();
    });
  }
});