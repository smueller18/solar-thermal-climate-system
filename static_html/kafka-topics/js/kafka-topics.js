
window.onload = function() {
  var jqxhr = $.get( "example.php", function() {
    alert( "success" );
    })
    .done(function() {
      alert( "second success" );
    })
    .fail(function() {
      alert( "error" );
    })
    .always(function() {
      alert( "finished" );
  });
}
