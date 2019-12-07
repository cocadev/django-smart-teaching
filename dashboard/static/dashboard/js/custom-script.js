 $(document).ready(function(e) {
        $(".showonhover").click(function(){
            $("#selectfile").trigger('click');
          });
          });


      var input = document.querySelector('input[type=file]'); // see Example 4

      input.onchange = function () {
        var file = input.files[0];

        drawOnCanvas(file);   // see Example 6
        displayAsImage(file); // see Example 7
      };

      function drawOnCanvas(file) {
        var reader = new FileReader();

        reader.onload = function (e) {
          var dataURL = e.target.result,
              c = document.querySelector('canvas'), // see Example 4
              ctx = c.getContext('2d'),
              img = new Image();

          img.onload = function() {
            c.width = img.width;
            c.height = img.height;
            ctx.drawImage(img, 0, 0);
          };

          img.src = dataURL;
        };

        reader.readAsDataURL(file);
      }

      function displayAsImage(file) {
        var imgURL = URL.createObjectURL(file),
            img = document.createElement('img');

        img.onload = function() {
          URL.revokeObjectURL(imgURL);
        };

        img.src = imgURL;
        document.body.appendChild(img);
      }

      $("#upfile1").click(function () {
          $("#file1").trigger('click');
      });
      $("#upfile2").click(function () {
          $("#file2").trigger('click');
      });
      $("#upfile3").click(function () {
          $("#file3").trigger('click');
      });



  newFunction();

function newFunction() {
  $('.js-pscroll').each(function () {
    var ps = new PerfectScrollbar(this);
    $(window).on('resize', function () {
      ps.update();
    });
  });
}
