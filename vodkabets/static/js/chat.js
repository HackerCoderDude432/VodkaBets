$(document).ready(function() {
  $(".chat").mouseenter(function() {
    $(this).stop().animate({ "margin-right": 0 }, "fast");
  }).mouseleave(function() {
    if ($(this).data("pinned", false)) {
      $(this).stop().animate({ "margin-right": -250 }, "fast");
    }
  });
})
