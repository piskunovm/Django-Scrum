function handleComplain() {
var denyReason = document.getElementById('denyReason');
    if (denyReason.value.length >= 1) {
    window.location.href = 'denied/?comment_moderator=' + denyReason.value;
    return false;
    }
};

function handleCorrection() {
    var correctionReason = document.getElementById('approveReason');
    if (correctionReason.value.length >= 1) {
        window.location.href = 'approve/?comment_moderator=' + correctionReason.value;
        return false;
    }
}

function checkApproveParams() {
    var approve_reason = $('#approveReason').val();

    if(approve_reason.length != 0) {
        $('#approve_button').removeAttr('disabled');
    } else {
        $('#approve_button').attr('disabled', 'disabled');
    }
}

function checkDenyParams() {
    var deny_reason = $('#denyReason').val();

    if(deny_reason.length != 0) {
        $('#deny_button').removeAttr('disabled');
    } else {
        $('#deny_button').attr('disabled', 'disabled');
    }
}