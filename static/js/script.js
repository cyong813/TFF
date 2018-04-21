$(document).ready(function(){
    $(".postComment").click(function(){
      let commentName = "#comment"+this.id;
        $(commentName).toggle();
    });
});
