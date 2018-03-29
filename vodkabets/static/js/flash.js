toastr.options = {
  "closeButton": true,
  "debug": false,
  "newestOnTop": true,
  "progressBar": true,
  "positionClass": "toast-top-right",
  "preventDuplicates": false,
  "onclick": null,
  "showDuration": "300",
  "hideDuration": "1000",
  "timeOut": "5000",
  "extendedTimeOut": "1000",
  "showEasing": "swing",
  "hideEasing": "linear",
  "showMethod": "fadeIn",
  "hideMethod": "fadeOut"
}

function flash(message, catagory) {
  if ($.inArray(catagory.toLowerCase(), ["success", "warning", "error"] > -1)) {
    toastr[catagory.toLowerCase()](message, catagory)
  } else {
    toastr.info(message, catagory)
  }
}
