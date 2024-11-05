/* Execution */
/* ========================================================================== */

// Bootstrap tooltips
bootstrapEnableTooltips()

// Mode toggle button
const modeToggler = document.getElementById("modeToggler");
setupModeToggler(modeToggler)

// Cookie Banner
const cookieBanner = document.getElementById("cookieBanner");
const force = false
showCookieBanner(cookieBanner, force);

// Timer banner
const timerBanner = document.getElementById("timerBanner");
const token = getCookie(tokenCookieName);
showSessionTimer(timerBanner, token);

// Sidebar
const sidebarPills = document.getElementsByClassName("side-link");
styleHoverPills(sidebarPills);

// Window scroll position saver (problematic because it also scrolls when changing site...)
// setPageScrollPositionListeners()
