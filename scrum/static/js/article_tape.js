var infinite = new Waypoint.Infinite({
    element: $('.infinite-container')[0],
    onBeforePageLoad: function () {
        $('.loading').show();
    },
    onAfterPageLoad: function ($items) {
        console.log($items)
        $('.loading').hide();
    }
});

console.log(infinite)

