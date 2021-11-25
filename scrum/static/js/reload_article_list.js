window.onload = function () {

    $('.article_card').on('click', '.dropdown_sorting_item', function (event) {
        var t_href = event.target;
        console.log(t_href.name)
        $.ajax({
            url: t_href.pathname,
            success: function (data) {
                $('.article_container').html(data.posts);
                document.querySelector('#dropdownMenuButton').innerHTML = (t_href.name);
                // document.getElementById('dropdownMenuButton').value = sorted_by;
                // document.querySelectorAll('.dropdown_sorting_item').forEach(n => n.classList.remove('bg-info'))
                // document.querySelectorAll('.dropdown_sorting_item').forEach(function (item) {
                //         if (item.id === sorted_by) {
                //             item.classList.add('bg-info')
                //         }
                //     }
                // )


            }
        });
        event.preventDefault();
    });
}