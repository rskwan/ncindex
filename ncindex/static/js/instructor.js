function selectcallback () {
    var cids = $("#courseSelect").val();
    $(".panel").each(function (index) {
        if (cids != null) {
            var showpanel = false;
            for (var j = 0; j < cids.length; j++) {
                showpanel = showpanel || $(this).hasClass("course" + cids[j]);
            }
            if (showpanel) {
                $(this).show();
            } else {
                $(this).hide();
            }
        } else {
            $(this).show();
        }
    });
}

$("th").addClass("text-center");
$(".chosen-select").chosen({width: "100%"});
$(".rating-panel").each(function (index) {
    var overall = parseInt($(this).find(".rating.overall").text());
    $(this).removeClass("panel-default");
    if (overall < 40) {
        $(this).addClass("panel-danger");
    } else if (overall < 70) {
        $(this).addClass("panel-warning");
    } else {
        $(this).addClass("panel-success");
    }
});
$(document).ready(function () {
    colorPanels();
    selectcallback();
});
$("#courseSelect").change(selectcallback);
