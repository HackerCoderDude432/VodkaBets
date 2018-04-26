var crashSocket = io.connect("/_crash")

// crash_bets_list update
crashSocket.on("update_crash_bets", (b64) => {
  // get json from b64 data
  var json = JSON.parse(atob(b64))

  //Generate html from data
  var newCrashBetsHTML = `
    <tr>
      <th>Username</th>
      <th>@</th>
      <th>Bet</th>
      <th>$</th>
    </tr>
  `

  // Only do if json is not empty, otherwise display a sad message
  if (json.length != 0) {
    $.each(json, (index, bet) => {
      $.each(bet, (index, value) => {
        if (value == null) {
          bet[index] = "-"
        }
      })

      newCrashBetsHTML += `
        <tr>
          <td>${bet.username}</td>
          <td>${bet.cashout_multiplier}</td>
          <td>${bet.amount}</td>
          <td>${bet.profit}</td>
        </tr>
      `
    })
  } else {
    newCrashBetsHTML += `
      <tr>
        <td>No bets have been placed yet :(</td>
      </td>
    `
  }

  //update the crash_bets_list
  $(".crash_bets_list").html(newCrashBetsHTML)
})

$(document).ready(function() {
  // Quick submit button functionality
  $("#crash_submit_bet").click(function() {
    crashSocket.emit("place_bet", $("#crash_bet_field").val(), "NOT IMPLEMENTED YET!!!!")
  })

  //Half button
  $("#crash_half").click(function() {
    var value = $("#crash_bet_field").val()

    // only divide if it is a number
    if ($.isNumeric(value)) {
      $("#crash_bet_field").val(Math.round(parseInt(value)/2))
    }
  })

  //Double button
  $("#crash_2x").click(function() {
    var value = $("#crash_bet_field").val()

    // only multiply if it is a number
    if ($.isNumeric(value)) {
      $("#crash_bet_field").val(Math.round(parseInt(value)*2))
    }
  })

  //Min button
  $("#crash_min").click(function() {
    // Set value to the field's minimum
    $("#crash_bet_field").val(parseInt($("#crash_bet_field").attr("min")))
  })

  //TODO: Make max button work
  //Max button
  $("#crash_min").click(function() {})
})
