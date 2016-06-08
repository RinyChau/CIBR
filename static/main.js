$("#searching").hide();
$("#results-table").hide();
$("#error").hide();

// global
//var url = 'http://static.pyimagesearch.com.s3-us-west-2.amazonaws.com/vacation-photos/dataset/';
//var data = [];

$(function() {

    // sanity check
    console.log("ready!");

    // image click
    $(".img").click(function() {
        $(".img").removeClass("active")
        // add active class to clicked picture
        $(this).addClass("active")

        // grab image url
        var url = $(this).attr("src")
        console.log(url)
        data = {url: url, img: null}
        searchImg(data);
    });

    $("#upload-image").submit(function (event) {
        // prevent default event
        event.preventDefault();

        var url = $("[name='_id_']").value;
        var img = $("#pic-src").files;

        if (!isURL(url) || (!img || !img[0])) {
            alert("please upload image first or enter the image url");
            return;
        }
        var formData = new FormData(this);
        searchImg(data);
    });

    $("#pic-src").change(function () {
        readURL($(this)[0]);
    });

    function isURL(str) {
        var pattern = new RegExp('^(https?:\\/\\/)?' + // protocol
            '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.?)+[a-z]{2,}|' + // domain name
            '((\\d{1,3}\\.){3}\\d{1,3}))' + // OR ip (v4) address
            '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' + // port and path
            '(\\?[;&a-z\\d%_.~+=-]*)?' + // query string
            '(\\#[-a-z\\d_]*)?$', 'i'); // fragment locator
        return pattern.test(str);
    }

    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#pic-preview')
                    .attr('src', e.target.result)
                    .width(150)
                    .height(200);
            };
            reader.readAsDataURL(input.files[0]);
        }
    }

    function searchImg(data) {

        // empty/hide results
        $("#results").empty();
        $("#results-table").hide();
        $("#error").hide();

        // show searching text
        $("#searching").show();
        console.log("searching...")

        // ajax request
        $.ajax({
            type: "POST",
            url: "/search",
            data: data,
            // handle success
            success: function(result) {
                console.log(result.results);
                var data = result.results;
                for (i = 0; i < data.length; i++) {
                    $("#results").append('<tr><th><a href="'+ data[i]["image"] + '"><img src="' + data[i]["image"] +
                        '" class="result-img"></a></th><th>' + data[i]['score'] + '</th></tr>')
                };
                $("#results-table").show();
            },
            // handle error
            error: function(error) {
                console.log(error);
                // append to dom
                $("#error").append(error)
            }
        });
    }

});
