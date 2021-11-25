var elm = document.getElementById('delete-profile');
elm.addEventListener('click', function () {
    window.location.href = '/auth/delete/?confirmed=true';
    return false;
});