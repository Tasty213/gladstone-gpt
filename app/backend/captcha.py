import os
from fastapi import HTTPException
from fastapi.datastructures import Address
from requests import post
from opentelemetry import trace

site_secret_default = os.getenv("RECHAPTCHA_SITE_SECRET")


class QuestionTooLongError(Exception):
    pass


def captcha_check(
    captcha_token: str,
    remote_ip: Address,
    site_secret: str = site_secret_default,
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
                "chatbot.captcha.status": str(success),
                "chatbot.captcha.challenge_ts": str(response.get("challenge_ts")),
                "chatbot.captcha.hostname": str(response.get("hostname")),
                "chatbot.captcha.error-codes": ",".join(response.get("error-codes")),
            },
        )

        if raise_on_fail:
            raise HTTPException(429, "error captcha check failed")

    return success is False


def throw_on_long_question(question: dict):
    sent_question = question.get("messages")[-1]

    if len(sent_question.get("content")) > 250:
        raise QuestionTooLongError
