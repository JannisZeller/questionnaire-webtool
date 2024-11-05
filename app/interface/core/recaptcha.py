import requests
from flask import Request, Response, current_app, redirect


from typing import Callable


def validate_recaptcha(req: Request, render: Callable[[], Response]):
    """Utility function for ReCaptcha-validation from a form.

    - Handles the ReCaptcha validation and renders the corresponding template.
    - The `render`-Callable needs to accept the following bollean
    keyword-agruments: `[recaptcha_failed, recaptcha_timedout]`
    - If the validation succeeds simply `1` is returned.
    """
    if not current_app.config["ENABLE_RECAPTCHA"]:
        return 1

    g_recaptcha_response = req.form.get("g-recaptcha-response")
    recaptcha_verify_url = (
        f"{current_app.config['RECAPTCHA_VERIFY_URL']}" +
        f"?secret={current_app.config['RECAPTCHA_PRIVATE_KEY']}" +
        f"&response={g_recaptcha_response}"
    )
    recaptcha_verify_res = None
    trys = 1
    while recaptcha_verify_res is None and trys <= 10:
        try:
            recaptcha_verify_res = requests.post(
                recaptcha_verify_url,
                timeout=1,
            ).json()
        except requests.exceptions.Timeout:
            trys += 1
            recaptcha_verify_res = None
            print("  ReCaptcha verification timed out. Retrying.")
        if trys == 10:
            return render(recaptcha_timedout=True)
    print(f"Info: ReCaptcha-Trys {trys}.")
    print(f"Info: ReCaptcha-Score {recaptcha_verify_res['score']}.")

    try:
        if recaptcha_verify_res["score"] < 0.5:
            return render(recaptcha_failed=True)
    except KeyError:
        return redirect(req.referrer)

    return 1
