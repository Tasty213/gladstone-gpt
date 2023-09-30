import os
from fastapi import HTTPException
from fastapi.datastructures import Address
from requests import post
from opentelemetry import trace

site_secret = os.getenv("RECHAPTCHA_SITE_SECRET")


def captcha_check(
    captcha_token: str,
    remote_ip: Address,
    site_secret: str = site_secret,
    raise_on_fail=True,
) -> bool:
    response = post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={
            "secret": site_secret,
            "response": captcha_token,
            "remoteip": remote_ip.host,
        },
        timeout=10,
    ).json()

    success = response.get("success")

    if not success:
        current_span = trace.get_current_span()
        current_span.add_event(
            "failed_captcha",
            attributes={
                "gladstone.captcha.status": str(success),
                "gladstone.captcha.challenge_ts": str(response.get("challenge_ts")),
                "gladstone.captcha.hostname": str(response.get("hostname")),
                "gladstone.captcha.error-codes": ",".join(response.get("error-codes")),
            },
        )

        if raise_on_fail:
            raise HTTPException(429, "error captcha check failed")

    return success is False
