$(document).ready(function(){
    $("input[type='radio']").click(function(){
      if (this.value == 1) {
         $("#groupPost").hide();
         $("input[name='friend_group_name']").prop('required',false);
      } else {
        $("#groupPost").show();
        $("input[name='friend_group_name']").prop('required',true);
      }
    });
});
