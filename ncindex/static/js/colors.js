$("td").filter(".rating").each(function (index) {
    var rating = parseInt($(this).text());
    if (rating < 40) {
        $(this).addClass("danger");
    } else if (rating < 70) {
        $(this).addClass("warning");
    } else {
        $(this).addClass("success");
    }
});
