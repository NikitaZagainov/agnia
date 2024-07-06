from src.actions.registry import register_action
from src.actions.user_messages.mail_messages import form_mail_message
from src.models.mail_params import MailInputParams, MailOutputParams
from src.external_services.llm import LLM
from email.parser import BytesParser
from email import policy
import imaplib
from concurrent.futures import ThreadPoolExecutor
import asyncio


imap_server = "mail.innopolis.ru"
port = 993
prompt = "You are given with an email: {}. Write a summarization with all important points included."
llm = LLM()


@register_action(
    MailInputParams,
    MailOutputParams,
    system_name="InnopolisMail",
    action_name="summarize_recent_mail",
    result_message_func=form_mail_message,
)
def summarize_recent_mail(
    authorization_data: dict, input_data: MailInputParams
) -> MailOutputParams:
    try:
        username = authorization_data["InnopolisMail"]["username"]
        password = authorization_data["InnopolisMail"]["password"]

    except Exception:
        return MailOutputParams(response="Not authenticated", error_code=1)

    try:
        mail = imaplib.IMAP4_SSL(imap_server, port)
        mail.login(username, password)
        mail.select("inbox")

        result, data = mail.uid("search", None, "(UNSEEN)")
        email_uid = data[0].split()[-1]

        result, data = mail.uid("fetch", email_uid, "(BODY[])")
        email_message = BytesParser(policy=policy.default).parsebytes(data[0][1])

    except Exception:
        return MailOutputParams(response="Error fetching mailbox", error_code=1)

    try:
        decoded_text = ""

        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                decoded_text += part.get_payload(decode=True).decode(
                    part.get_content_charset()
                )

    except Exception:
        return MailOutputParams(response="Error decoding email content", error_code=1)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            lambda: asyncio.run(
                llm.get_response({"prompt": prompt.format(decoded_text)})
            )
        )
    response = future.result()
    return MailOutputParams(response=response, error_code=0)
