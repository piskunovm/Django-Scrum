var elm_publish = document.getElementById('publish_post');
elm_publish.addEventListener('click', function () {
    window.location.href = 'published';
    return false;
});


// var elm_correction = document.getElementById('correction_post');
// elm_correction.addEventListener('click', function () {
//     var correctionReason = document.getElementById('correctionReason');
//     console.log(correctionReason.value);
//     window.location.href = 'correction/?comment_moderator=' + correctionReason.value;
//     return false;
// });


function handleCorrection() {
    var correctionReason = document.getElementById('correctionReason');
    if (correctionReason.value.length >= 1) {
        window.location.href = 'correction/?comment_moderator=' + correctionReason.value;
        return false;
    }
}

