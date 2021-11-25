set_audio_block = function () {
    var article_id = parseInt(document.getElementById("container_audio_block").getAttribute("name"));
    var url = '/post/get_audio_block/';
    var data = {
        article_id: article_id
    };

    $.ajax({
        url: url,
        data: data,
        success: function (data) {
            if (data.status === 'generating') {
                setTimeout(set_audio_block, 10000);
            } else {
                if (data.status === 'done') {
                    $('#container_audio_block').html(data.audio_block);
                } else if (data.status === 'error') {
                    $('#container_audio_block').html(data.audio_block);
                }
                regenerate_button_click();
            }
        }
    });
}

start_set_audio_block = function (article_id) {
    if (article_id !== 'done') {
        set_audio_block();
    } else {
        regenerate_button_click();
    }
}

regenerate_button_click = function () {
    var regenerate_button = document.getElementById('regenerate_audio');
    regenerate_button.addEventListener('click', function () {
        var article_id = regenerate_button.getAttribute("name");
        var container_audio_block = document.getElementById("container_audio_block");
        container_audio_block.innerHTML = '<p className = "fst-italic text-secondary" > Аудиодорожка генерируется...</p>';
        container_audio_block.setAttribute("name", article_id);
        var url = '/post/regenerate_audio/';
        var data = {
            article_id: article_id
        };

        $.ajax({
            url: url,
            data: data,
            success: function (data) {
                set_audio_block()
                start_set_audio_block(article_id);
            }
        });
        return false;
    });
}

window.onload = function () {
    var article_id = document.getElementById("container_audio_block").getAttribute("name");
    start_set_audio_block(article_id);
}
