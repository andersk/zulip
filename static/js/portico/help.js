import {activate_correct_tab} from "./tabbed-instructions.js";

function registerCodeSection($codeSection) {
    const $li = $codeSection.find("ul.nav li");
    const $blocks = $codeSection.find(".blocks div");

    $li.on("click", function () {
        const language = this.dataset.language;

        $li.removeClass("active");
        $li.filter("[data-language=" + language + "]").addClass("active");

        $blocks.removeClass("active");
        $blocks.filter("[data-language=" + language + "]").addClass("active");
    });
}

function highlight_current_article() {
    $(".help .sidebar a").removeClass("highlighted");
    const path = window.location.pathname;

    if (!path) {
        return;
    }

    const hash = window.location.hash;
    let article = $('.help .sidebar a[href="' + path + hash + '"]');
    if (!article.length) {
        // If there isn't an entry in the left sidebar that matches
        // the full url+hash pair, instead highlight an entry in the
        // left sidebar that just matches the url part.
        article = $('.help .sidebar a[href="' + path + '"]');
    }
    // Highlight current article link and the heading of the same
    article.closest("ul").css("display", "block");
    article.addClass("highlighted");
}

function render_code_sections() {
    $(".code-section").each(function () {
        activate_correct_tab($(this));
        registerCodeSection($(this));
    });

    highlight_current_article();

    common.adjust_mac_shortcuts(".markdown .content code", true);

    $("table").each(function () {
        $(this).addClass("table table-striped");
    });
}

$(".sidebar.slide h2").on("click", (e) => {
    const $next = $(e.target).next();

    if ($next.is("ul")) {
        // Close other article's headings first
        $(".sidebar ul").not($next).hide();
        // Toggle the heading
        $next.slideToggle("fast", "swing");
    }
});

if (window.location.pathname === "/help/") {
    // Expand the Guides user docs section in sidebar in the /help/ homepage.
    $(".help .sidebar h2#guides + ul").show();
}
// Remove ID attributes from sidebar links so they don't conflict with index page anchor links
$(".help .sidebar h1, .help .sidebar h2, .help .sidebar h3").removeAttr("id");

// Scroll to anchor link when clicked
$(document).on(
    "click",
    ".markdown .content h1, .markdown .content h2, .markdown .content h3",
    function () {
        window.location.hash = $(this).attr("id");
    },
);

$(".hamburger").on("click", () => {
    $(".sidebar").toggleClass("show");
});

$(".markdown").on("click", () => {
    if ($(".sidebar.show").length) {
        $(".sidebar.show").toggleClass("show");
    }
});

render_code_sections();

$("body").addClass("noscroll");
