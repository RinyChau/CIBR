$(function () {
    console.log("ready!");

    $(".silimar-search").click(function () {
        // grab image url
        var url = $(this).attr("img-src")
        console.log(url)
        data = {url: url, img: null}
        searchImg(data);
    });

    $("#pic-src").change(function () {
        readURL($(this)[0]);
        uploadImg = true;
    });

    var uploadImg = true;
    $("#pic-url").change(function () {
        $('#pic-preview').attr('src', this.value);
        $('#pic-preview').show();
        uploadImg = false;
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
                    .attr('src', e.target.result);
                $('#pic-preview').show();
            };
            reader.readAsDataURL(input.files[0]);
        }
    }


    $("#upload-image").submit(function (event) {
        // prevent default event
        event.preventDefault();

        var url = $("#pic-url").val();
        var img = $("#pic-src")[0].files;
        if (uploadImg && (!img || !img[0])) {
            alert("please upload image first or enter the image url");
            return;
        }
        if (!uploadImg && !isURL(url)) {
            alert("please upload image first or enter the image url");
            return;
        }
        if (!isURL(url) && (!img || !img[0])) {
            alert("please upload image first or enter the image url");
            return;
        }
        var formData = new FormData($("#upload-image")[0]);
        if (!uploadImg) {
            formData.delete("img");
        }
        searchImg(formData);
    });


    $("#upload_img_submit").click(function () {
        event.preventDefault();
        $("#upload-image").submit();
    });


    function searchImg(data) {

        // empty/hide results
        $("#img_gallery").html("");
        //$("#results").empty();
        //$("#results-table").hide();
        //$("#error").hide();

        // show searching text
        $("#searching").show();
        console.log("searching...")
        var ajaxParam = {
            type: "POST",
            url: "/search",
            data: data,
            // handle success
            success: function (result) {
                console.log(result.results);
                var data = result.results;
                for (i = 0; i < data.length; i++) {
                    var html_str = "<div class='col-lg-3 col-md-4 col-xs-6 thumb'><div class='hovereffect'>";
                    html_str += "<a class='thumbnail' href='#'>" + "<img class='img-responsive' src='" + data[i]["path"] + "' alt=''>" + " </a>";
                    html_str += "<div class='overlay'><h2>Label: " + data[i]['labels']['label1'] + "</h2><h2>probability: " + data[i]['labels']['prob1'] + "</h2>";
                    html_str += "<h2>Distance: " + data[i]['distance'] + "</h2>"
                    html_str += "<a class='info silimar-search' href='#' img-src='" + data[i]["path"] + "'>similar</a>";
                    html_str += "</div>"
                    html_str += "</div></div>";
                    $("#img_gallery").append(html_str);
                };
            },
            // handle error
            error: function (error) {
                console.log(error);
                window.alert("can not retrieve image, please try again later");
            },
            //Options to tell jQuery not to process data or worry about content-type.
            cache: false,
        };
        if (!data.url) {
            ajaxParam.contentType = false;
            ajaxParam.processData = false;
        }
        //ajax request
        $.ajax(ajaxParam);

    }
});
