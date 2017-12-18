function delete_memo(value) {
  console.log("Delete button clicked");
  var token = value;
  console.log(token);
  $.ajax({
    url: DEL_MEMO,
    data: {token: token},
    success: function () {
      console.log("Add: Got a response!");
      location.href = "/";
    }
  });
};