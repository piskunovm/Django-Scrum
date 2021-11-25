handleSearch = function () {
    var filter = document.querySelector('#search_filters .active').id;
    var search_request = document.querySelector('#search_request').value;
    var url = '/search/?search_request=' + search_request + '&filter=' + filter;
    window.location.href = url;
}

window.onload = function () {

    $('.search_filters').on('click', '.nav-item', function (event) {
        var t_href = event.target;
        var url = t_href.pathname;
        var filter = t_href.id;
        var data = {
            filter: filter,
            search_request: document.querySelector('#search_request').value
        };
        $.ajax({
            url: url,
            data: data,
            success: function (data) {
                $('.search_output').html(data.search_output);
                var filter_items = document.querySelectorAll('ul.nav li a');
                for (i = 0; i < filter_items.length; ++i) {
                    filter_items[i].classList.remove('active');
                    filter_items[i].classList.remove('shadow');
                    filter_items[i].classList.remove('rounded');
                }
                var active_link = document.querySelector('#' + filter);
                active_link.classList.add('active');
                active_link.classList.add('shadow');
                active_link.classList.add('rounded');
            }
        });
        event.preventDefault();
    });
};