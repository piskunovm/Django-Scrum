function handleBan() {
    var banReason = document.getElementById('reason');
    var banTime = document.getElementById('ban_time');
    var banDescription = document.getElementById('ban_description');
    var pk = document.getElementById('user_id');
    if (banReason.value.length >= 1) {
        window.location.href = 'ban/?reason=' + banReason.value & '/?banDescription=' + banDescription.value & '/?pk=' + pk.value & '/?ban_time=' + banTime.value;
        return false;}
};

//function handleCorrection() {
//    var correctionReason = document.getElementById('approveReason');
//    if (correctionReason.value.length >= 1) {
//        window.location.href = 'approve/?comment_moderator=' + correctionReason.value;
//        return false;
//    }
//}

