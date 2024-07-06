from src.actions.registry import register_action
from src.actions.user_messages.mail_messages import form_mail_message
from src.models.mail_params import MailInputParams, MailOutputParams
from src.models.prompts import EMAIL_SUMMARIZATION_PROMPT
from src.external_services.llm import LLM
import email
from email.header import decode_header
import imaplib
from concurrent.futures import ThreadPoolExecutor
import asyncio


imap_server = "mail.innopolis.ru"
port = 993
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
    """
    Fetches and summarizes the most recent email from the user's inbox.

    Args:
        authorization_data (dict): A dictionary containing the user's
            authorization data.
        input_data (MailInputParams): Input parameters for the action.

    Returns:
        MailOutputParams: The output parameters of the action.

    Raises:
        None
    """

    try:
        username = authorization_data["InnopolisMail"]["username"]
        password = authorization_data["InnopolisMail"]["password"]

    except Exception:
        return MailOutputParams(response="Not authenticated", error_code=1)

    try:
        mail = imaplib.IMAP4_SSL(imap_server, port)
        mail.login(username, password)
        mail.select("inbox")

        _, data = mail.search(None, "(UNSEEN)")

        latest_email_id = data[0].split()[-1]

        _, data = mail.fetch(latest_email_id, "(RFC822)")

        email_message = email.message_from_bytes(data[0][1])

        subject = decode_header(email_message["Subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()

        # Fetch the internal date (received time)
        time = mail.fetch(latest_email_id, "(INTERNALDATE)")[1][0].decode()
        time = time[time.index('"') + 1 : time.rindex('"')]

        # Fetch the sender
        sender = email_message.get("From")

        # Fetch the email body
        # This part might need adjustments based on the email structure
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain" or content_type == "text/html":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = email_message.get_payload(decode=True).decode()

    except IndexError:
        return MailOutputParams(
            subject=None,
            time=None,
            sender=None,
            body="No new emails",
            error_code=1,
        )

    except Exception:
        return MailOutputParams(
            subject=None,
            time=None,
            sender=None,
            body="Failed to fetch email",
            error_code=1,
        )

    try:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(
                lambda: asyncio.run(
                    llm.get_response({"prompt": body + EMAIL_SUMMARIZATION_PROMPT})
                )
            )

        response = future.result()

    except Exception:
        return MailOutputParams(
            subject=None,
            time=None,
            sender=None,
            body="Failed to summarize email",
            error_code=1,
        )

    return MailOutputParams(
        subject=subject, time=time, sender=sender, body=response, error_code=0
    )

