/**
 * Created by Ellis on 15/09/2016.
 */

//Script function for newMenu.html
function source_select() {
    if (document.getElementById('local_source').checked) {
        document.getElementById('ifLocal').style.display = 'block';
        document.getElementById('ifURL').style.display = 'none';
    } else if (document.getElementById('url_source').checked) {
        document.getElementById('ifURL').style.display = 'block';
        document.getElementById('ifLocal').style.display = 'none';
    } else if (document.getElementById('no_cover').checked) {
        document.getElementById('ifLocal').style.display = 'none';
        document.getElementById('ifURL').style.display = 'none';
    }
}