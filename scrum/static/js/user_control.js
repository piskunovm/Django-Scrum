window.onload = function () {

    $('.form-check').on('click', '.inputUserStatus', function (event) {
        var t_href = event.target;
        var user_id = t_href.closest('tr').id;
        var current_status
        $.ajax({
            url: 'get/' + user_id + '/',
            success: function (data) {
                current_status = data.user.user_status;
                t_href.checked = current_status;

                $('#changeUserStatus-modal-' + user_id).modal('toggle');
                $('#changeUserStatus-modal-' + user_id + ' span.status').each(function () {
                    if (t_href.checked === true) {
                        this.innerHTML = "Деактивировать"
                    } else {
                        this.innerHTML = "Активировать"
                    }
                });
            }
        });


        event.preventDefault();
    });

    $('.user_status').on('click', ".switchUserStatus", function (event) {
        var user_id = event.target.closest('div').id.split('-')[1];
        var switch_elm = document.getElementById("inputUserStatus-" + user_id)
        $.ajax({
            url: 'delete/' + user_id + '/',
            success: function (data) {
                switch_elm.checked = data.user_is_active_status;
                $('#changeUserStatus-modal-' + user_id).modal('hide');
            }
        });
        event.preventDefault();
    });

    $('.user_role').on('change', '.selectUserRole', function (event) {
        var t_href = event.target;
        var user_id = t_href.closest('tr').id;
        var new_role = t_href.value;
        t_href.name = new_role;
        var current_role;
        $.ajax({
            url: 'get/' + user_id + '/',
            success: function (data) {
                current_role = data.user.user_role;
                t_href.value = current_role;
            }
        });

        $('#changeUserRole-modal-' + user_id).modal('toggle');
        $('#changeUserRole-modal-' + user_id + ' span.role').each(function () {
            if (new_role === "administrator") {
                this.innerHTML = "Администратор"
            } else if (new_role === "user") {
                this.innerHTML = "Обычный пользователь"
            } else if (new_role === "moderator") {
                this.innerHTML = "Модератор"
            }
        });
        event.preventDefault();
    });

    $('.user_role').on('click', ".switchUserRole", function (event) {
        var user_id = event.target.closest('div').id.split('-')[1];
        var switch_elm = document.getElementById("selectUserRole-" + user_id)
        var new_role = switch_elm.name;
        $.ajax({
            url: 'role/' + user_id + '/' + new_role + '/',
            success: function (data) {
                switch_elm.value = data.user_role;
                $('#changeUserRole-modal-' + user_id).modal('hide');
            }
        });
        event.preventDefault();
    });

}