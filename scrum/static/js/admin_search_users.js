handleSearch = function () {
    var search_request = document.querySelector('#search_request').value;
    var url = '/my_admin/search/';
    var data = {
        filter: 'users',
        search_request: search_request
    };
    $.ajax({
        url: url,
        data: data,
        success: function (data) {
            $('.admin_users_list').html(data.search_output);
        }
    });
}

var reset_button = document.getElementById('reset_search');
reset_button.addEventListener('click', function () {
    var search_request = document.querySelector('#search_request');
    search_request.value = '';
    handleSearch();
    return false;
});
