// Ajax request for generating report
async function genRepAJAX() {
    const form = document.getElementById("genRepForm");
    const loaderContainer = document.getElementById("loaderContainer");
    const previousResults = document.getElementById("results");

    try {
        previousResults.classList.add("d-none");
        loaderContainer.classList.remove("d-none");
        const res = await fetch(form.action, {
            method: form.method,
            headers: {
                'Content-Type': 'application/json'
            },
        });
        console.log(res)

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


var button = document.getElementById("genRepBtn");
button.onclick = () => {
    var res = genRepAJAX();
    res.then(() => {
        console.log("Success");
        window.location.reload();
    })
}
