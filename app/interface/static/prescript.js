/* Globals / Utils */
/* -------------------------------------------------------------------------- */
const consentCookieName = "x-consent";
const tokenCookieName = "x-access-token";


// Util functions
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop().split(';').shift();
    }
    else {
        return null;
    }
}

function decodeJWT(token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    var jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload);
}


/* Bootstrap: enabling tooltips */
/* -------------------------------------------------------------------------- */
function bootstrapEnableTooltips() {
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}


/* Theming */
/* -------------------------------------------------------------------------- */
function getStoredTheme() { sessionStorage.getItem('theme'); }
function setStoredTheme(theme) { sessionStorage.setItem('theme', theme); }

function getPreferredTheme() {
    const storedTheme = getStoredTheme();
    if (storedTheme) {
      return storedTheme;
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function getCurrentTheme() {
    return document.documentElement.getAttribute('data-bs-theme');
}

function setFooterTheme(dark_light) {
    console.log("no footer");
    // if (dark_light === "dark") {
    //     document.getElementById("footer").classList.remove("bg-light");
    //     document.getElementById("footer").classList.add("bg-dark");
    // }
    // if (dark_light === "light") {
    //     document.getElementById("footer").classList.remove("bg-dark");
    //     document.getElementById("footer").classList.add("bg-light");
    // }
}

function setDocumentTheme(dark_light) {
    document.documentElement.setAttribute('data-bs-theme', dark_light);
}

function setDocThemePreLoad() {
    setDocumentTheme(getPreferredTheme());
}

function setFooterThemePrelaod() {
    setFooterTheme(getPreferredTheme());
}

function setThemeTogglerThemePrelaod() {
    const modeToggler = document.getElementById("modeToggler");
    const theme = document.documentElement.getAttribute('data-bs-theme');
    if (theme === "light") {
        modeToggler.checked = false;
    }
    if (theme === "dark") {
        modeToggler.checked = true;
    }
}

// Toggle button:
function setupModeToggler(modeToggler) {
    if (modeToggler === null) {
        return 0;
    }
    modeToggler.addEventListener('change', e => {
        const theme = e.target.checked? "dark" : "light";
        setDocumentTheme(theme);
        setFooterTheme(theme);
        setStoredTheme(theme);
    });
}


/* Cookie Consent */
/* -------------------------------------------------------------------------- */
function showCookieBanner(cookieBanner, force) {
    if (cookieBanner === null) {
        return 0;
    }
    const consentCookie = getCookie(consentCookieName);
    if (consentCookie === "1" && !force) {
        cookieBanner.classList.add("d-none");
    }
    else { }
}


/* Session timer */
/* -------------------------------------------------------------------------- */
function setSessionTimer(timerBanner) {
    var exp = Date.parse( sessionStorage.getItem("loginExp") );
    var now = new Date(Date.now());
    var diff = exp - now;

    var minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((diff % (1000 * 60)) / 1000);

    timerBanner.innerHTML = ('0'+minutes).slice(-2) + ":" + ('0'+seconds).slice(-2);

    return diff;
}

function setTimerExp(token) {
    const tokenDecoded = decodeJWT(token);
    const exp = new Date(1000 * tokenDecoded["exp"]);
    sessionStorage.setItem("loginExp", exp)
}

function showSessionTimer(timerBanner, token) {
    if (timerBanner === null) {
        return 0;
    }
    if (token === null) {
        return 0;
    }
    setTimerExp(token);
    var x = setInterval(function() {
        diff = setSessionTimer(timerBanner);
        if (diff < 0) {
            clearInterval(x);
            timerBanner.innerHTML = "00:00";
        }
    }, 1000);
}


/* Window scroll position saver */
/* -------------------------------------------------------------------------- */
function setPageScrollPositionListeners() {
    // Alternative: document.addEventListener("DOMContentLoaded", function (ev) {
    //  is not practical with images
    window.addEventListener("load", function (ev) {
        var scrollYPos = sessionStorage.getItem('scrollYPos');
        if (scrollYPos) {
            console.log(`Scrolling page to ${scrollYPos}`);
            window.scrollTo({
                top: scrollYPos,
                left: 0,
                behavior: 'instant',
              });
            sessionStorage.removeItem('scrollYPos');
        }
    });

    window.addEventListener("beforeunload", function (e) {
        sessionStorage.setItem('scrollYPos', window.scrollY);
    });
}


/* Sidebar */
/* -------------------------------------------------------------------------- */
function sidePillMouseover(event) {
    event.target.classList.add("active");
}

function sidePillMouseout(event) {
    event.target.classList.remove("active");
}

function styleHoverPills(pills) {
    if (pills.length == 0) {
        return 0;
    }
    for(var idx=0; idx < pills.length; idx++){

        var sidebarPill = pills[idx];

        if (!sidebarPill.classList.contains("active")) {
            sidebarPill.addEventListener("mouseover", sidePillMouseover);
            sidebarPill.addEventListener("mouseout", sidePillMouseout);
        }
    }
}


/* User Deletion Confirm Button */
/* -------------------------------------------------------------------------- */
function uncheckUserDeletionConfirm() {
    const confirmDeletionCheckbox = document.getElementById("confirmUserDeletionCheckbox");
    confirmDeletionCheckbox.checked = false;
}

function confirmUserDeletion() {
    const userDeleteButton = document.getElementById("userDeleteButton");
    const confirmUserDeletionCheckbox = document.getElementById("confirmUserDeletionCheckbox");

    if (confirmUserDeletionCheckbox.checked) {
        userDeleteButton.classList.remove("disabled");
        userDeleteButton.setAttribute("aria-disabled", "false");
    }
    else {
        userDeleteButton.classList.add("disabled");
        userDeleteButton.setAttribute("aria-disabled", "true");
    }
}


/* Item Scroller */
/* -------------------------------------------------------------------------- */
function scrollActiveItemIntoView() {
    console.log("Scrolling active item into view")
    const itemScrollPills = document.getElementsByClassName("view-scrollpill");
    for(var idx=0; idx < itemScrollPills.length; idx++){
        var itemScrollPill = itemScrollPills[idx];
        if (itemScrollPill.classList.contains("active")) {
            itemScrollPill.scrollIntoView({
                behavior: 'instant',
                block: 'center',
                inline: 'center'
            });
        }
    }
}


/* Submitters for Item-Forms */
/* -------------------------------------------------------------------------- */
async function submitItemAJAX(item) {
    const itemNameArr = item.name.split("-")
    const itemName = itemNameArr[0];
    const form = item.form;

    if (item.type == "textarea") {
        var response = item.value;
        var itemType = "text";
    }
    if (item.type == "checkbox") {
        var itemType = "mc";
        var response = itemNameArr[1];
        if (response == "1") {
            var oppositeItemName = itemName + "-0";
            var response = true;
        }
        if (response == "0") {
            var oppositeItemName = itemName + "-1";
            var response = false;
        }
        var oppositeItem = document.getElementById(oppositeItemName);
        oppositeItem.checked = false;
    }
    if (item.type == "file") {
        var canvasElement = document.getElementById(itemName + "-canvas");
        var response = canvasElement.toDataURL("image/png", 1.);
        response = response.replace(/^(data:image\/jpeg\;base64\,)/,"");
        console.log("Submitting image");
        var itemType = "image"
    }

    try {
        const res = await fetch(form.action, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            // credentials: 'include',
            body: JSON.stringify({
                response: response,
                item_type: itemType
            })
        });

        // Updating session timer because AJAX also sets token-cookie
        try {
            const token = getCookie(tokenCookieName);
            setTimerExp(token);
        } catch (error) {
            console.log("Error updating the session timer on AJAX req:\n\t");
            console.log(error);
        }

        if (res.status == 410) {
            window.location.replace("/");
        }
    } catch (error) {
        alert(`Es gab einen Fehler bei der Verarbeitung ihrer Eingabe: ${error}`);
    }
}


/* Execution */
/* ========================================================================== */
