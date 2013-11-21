/**
 * Created by khoatran on 11/20/13.
 */
$(document).ready(function() {
    bindPageNav();
    bindZingTvForm();
    bindZingMp3Form();
});

function bindZingTvForm() {
    $("#zing_tv_form").submit(function(ev) {
        ev.preventDefault();
        $.ajax({
            url: '/zingtv',
            data: {'series': $('#zing_tv_album').val()},
            success: function(data) {
                if (data.ok) {
                    // Build downloads section
                    var html = '<ul>';
                    data.movies.forEach(function(item) {
                        var name = item.name;
                        html += '<li><a href="' + item.url + '" download="'
                            + name + '.mp4' + '">' + name +'</a></li>';
                    });
                    html += '</ul>';
                    $("#zing_tv_downloads").html(html);
                    // Build links section
                    var $links = $("#zing_tv_links");
                    data.movies.forEach(function(item) {
                        $links.append(item.url + "<br>");
                    });
                }
            },
            error: function(xhr, status, err) {
                showErrorAlert($("#zing_tv_error"), err);
            }
        });
    });
}

function bindZingMp3Form() {
    $("#zing_mp3_form").submit(function(ev) {
        ev.preventDefault();
        $.ajax({
            url: '/zingmp3',
            data: {'album': $('#zing_mp3_album').val()},
            success: function(data) {
                if (data.ok) {
                    // Build downloads section
                    var html = '<ul>';
                    data.mp3.forEach(function(item) {
                        var name = item.title + ' - ' + item.artist;
                        html += '<li><a href="' + item.url + '" download="'
                            + name + '.mp3' + '">' + name +'</a></li>';
                    });
                    html += '</ul>';
                    $("#zing_mp3_downloads").html(html);
                    // Build links section
                    var $links = $("#zing_mp3_links");
                    data.mp3.forEach(function(item) {
                        $links.append(item.url + "<br>");
                    });
                }
            },
            error: function(xhr, status, err) {
                showErrorAlert($("#zing_mp3_error"), err);
            }
        });
    });
}

function bindPageNav() {
    $(".ga-nav-page").click(function() {
        var $page = $("#" + $(this).attr('data-page'));
        $("div.page").hide();
        $page.fadeIn();
        $(".ga-nav-page").removeClass("active");
        $(this).addClass("active");
    });

    $(".ga-nav-page.active").trigger('click');
}

function showErrorAlert(parent, message) {
    var $alert = $('<div>', {'class': 'alert alert-danger'}).appendTo(parent);
    var $close = $('<button>', {'type': 'button', 'class': 'close',
        'data-dismiss': 'alert', 'aria-hidden': 'true'}).appendTo($alert)
        .html('&times;');
    var $content = $('<p>').text(message).appendTo($alert);
}
