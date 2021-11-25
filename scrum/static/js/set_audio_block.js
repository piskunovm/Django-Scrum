set_audio_block = function () {
    var article_id = parseInt(document.getElementById("audio_block").getAttribute("name"));
    var url = '/post/get_audio_block/';
    var data = {
        article_id: article_id
    };

    $.ajax({
        url: url,
        data: data,
        success: function (data) {
            if (data.status === 'done') {
                $('#audio_block').html(data.audio_block);
            } else if (data.status === 'error') {
                $('#audio_block').html(data.audio_block);
            } else if (data.status === 'generating') {
                setTimeout(set_audio_block, 10000);
            }
        }
    });
}

window.onload = function () {
    var article_id = document.getElementById("audio_block").getAttribute("name");
    if (article_id !== 'done') {
        set_audio_block();
    }
}
