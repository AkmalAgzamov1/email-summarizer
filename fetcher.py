from datetime import datetime
from email.utils import parsedate_to_datetime

from models import Email, Provider
from parser import extract_body


def get_new_emails(service, max_results=10) -> list[Email]:
    """
    Fetch emails from Gmail API and convert them into Email objects.
    """

    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=max_results
        )
        .execute()
    )


    message_ids = [
        message["id"]
        for message in response.get("messages", [])
    ]


    emails = []


    for message_id in message_ids:

        try:
            raw_message = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=message_id,
                    format="full"
                )
                .execute()
            )


            email = _parse_message(raw_message)

            emails.append(email)


        except Exception as error:

            print(
                f"Failed to parse email {message_id}: {error}"
            )

            continue


    return emails



def _parse_message(raw: dict) -> Email:
    """
    Convert Gmail JSON message into our Email dataclass.
    """


    payload = raw["payload"]


    headers = {
        header["name"]: header["value"]
        for header in payload.get("headers", [])
    }


    body = extract_body(payload)


    date_string = headers.get("Date")


    if date_string:
        try:
            received_at = parsedate_to_datetime(date_string)

        except Exception:
            received_at = datetime.now()

    else:
        received_at = datetime.now()



    return Email(
        id=raw["id"],
        provider=Provider.GMAIL,
        sender=headers.get("From", "Unknown"),
        subject=headers.get("Subject", "No subject"),
        body_text=body,
        received_at=received_at
    )