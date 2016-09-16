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

//Form validation
function validateForm() {
    var x = document.forms["frmContact"]["collection"].value;

    if (x == null || x == "") {
        document.getElementById("fName").className = document.getElementById("fName").className + " error";
        document.getElementById("errorMessage").style.color = "indianred";
        document.getElementById("errorMessage").innerHTML = "Please input a collection name!";
        return false;
    } else {
        document.getElementById("fName").className = document.getElementById("fName").className.replace(" error", "");
        document.getElementById("errormessage").innerHTML = "";
        return true;
    }
}