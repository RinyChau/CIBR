$(function () {
    console.log("ready!");

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
        $("#label_prob").html("");
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
                var data = result["data"];
                var labels = result["labels"];
                for (var i = 0; i < data.length; i++) {
                    var html_str = "<div class='col-lg-3 col-md-4 col-xs-6 thumb'><div class='hovereffect'>";
                    html_str += "<a class='thumbnail' href='#'>" + "<img class='img-responsive' src='" + data[i]["path"] + "' alt=''>" + " </a>";
                    html_str += "<div class='overlay'><h2>Label: " + data[i]['labels']['label1'] + "</h2><h2>probability: " + data[i]['labels']['prob1'].toFixed(2) + "</h2>";
                    html_str += "<h2>Distance: " + data[i]['distance'].toFixed(2) + "</h2>"
                    html_str += "<a class='info silimar-search' href='#' img-src='" + data[i]["path"] + "'>similar</a>";
                    html_str += "</div>"
                    html_str += "</div></div>";
                    $("#img_gallery").append(html_str);
                }
                ;

                for (var i = 1; i <= 5; i++) {
                    var label = labels["label" + i]
                    var prob = labels["prob" + i]
                    var html_str = "<strong style='color: #000;font-weight: initial;'>" + label + "</strong>";
                    html_str += "<span class='pull-right' style='color: black;'>" + (prob * 100).toFixed(2) + "%</span>"
                    html_str += '<div class="progress"> <div class="progress-bar" role="progressbar" aria-valuenow="' +
                        Math.round(prob * 100) + '" aria-valuemin="0" aria-valuemax="100" style="width:' +
                        Math.round(prob * 100) + '%">' + '</div> </div>'
                    $("#label_prob").append(html_str);
                }

                $(".silimar-search").click(function () {
                    // grab image url
                    console.log(url)
                    var url = $(this).attr("img-src");
                    $('#pic-preview').attr('src', url);
                    data = {url: url, img: null}
                    searchImg(data);
                });
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
