var images = document.getElementsByTagName("img");
// console.log(images)
var i;

for (i = 0; i < images.length; i++) {
    // console.log(images[i].outerHTML)
    // images[i].className += " article_image article_img img-fluid bg-white rounded";
    images[i].style.width = null;
    images[i].style.height = null
    // images[i].outerHTML = '<div class="container article_card blog-article w-container p-3 bg-white rounded" style="margin: 20px auto 0 auto; max-width: 960px;">' + images[i].outerHTML + '</div>';

}