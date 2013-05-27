
$('.jobtable .btn').popover();

$('.jobtable input:checkbox').click(function() {
  $(this).parents('tr').toggleClass('marked');
});
