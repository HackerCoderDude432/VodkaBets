var chatSocket = io.connect("/_chat")

chatSocket.on("update_chat_count", (number) => {
  $("#chat_count").html("Online: " + number)
})

chatSocket.on("process_message", (user, message) => {
  $("#chat_main").append("<b>" + user + ": </b><span>" + message + "</span><br>")
  $('#chat_main').scrollTop($('#chat_main')[0].scrollHeight - $('#chat_main')[0].clientHeight)
})

chatSocket.on("flash", (message, catagory) => {
  flash(message, catagory)
})

$(document).ready(function() {
  // hiding of chat panel
  var pinned = false
  $(".chat").mouseenter(function() {
    $(this).stop().animate({ "margin-right": 0 }, "fast");
  }).mouseleave(function() {
    if (!pinned) {
      $(this).stop().animate({ "margin-right": -250 }, "fast");
    }
  })

  //Pin button
  $("#chat_pin").click(function() {
    if (!pinned) {
      $(this).html("Unpin")
    } else {
      $(this).html("Pin")
    }
    pinned = !pinned
  })

  // Code that submits the message to the server
  $("#chat_send").click(function () {
    var message = $("#chat_input").val()
    if (message) {
      chatSocket.emit("send_message", message)
      $("#chat_input").val(null) //Clear textarea afterwards
    }
  })

  // Map enter in the textarea to do the same thing
  $('#chat_input').keypress(function(e) {
    if (e.which == 13) { //Enter key pressed
      e.preventDefault()
      $('#chat_send').click();
    }
  });
})
