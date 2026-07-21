import base64

from bs4 import BeautifulSoup


def decode_body(data: str) -> str:
    """
    Gmail stores email body as base64url.
    Convert it into normal text.
    """

    # Gmail sometimes removes "=" padding
    padding = "=" * (-len(data) % 4)

    decoded_bytes = base64.urlsafe_b64decode(
        data + padding
    )

    return decoded_bytes.decode(
        "utf-8",
        errors="ignore"
    )



def html_to_text(html: str) -> str:
    """
    Convert HTML email into readable text.
    """

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    return soup.get_text(
        separator="\n",
        strip=True
    )



def extract_body(payload: dict) -> str:
    """
    Extract readable email body from Gmail payload.

    Priority:
    1. text/plain
    2. text/html -> converted into text

    Ignores attachments.
    """


    plain_text = None
    html_text = None



    mime_type = payload.get(
        "mimeType"
    )


    body = payload.get(
        "body",
        {}
    )


    # Case 1:
    # Non-multipart email
    #
    # Example:
    # payload:
    # {
    #    "mimeType": "text/html",
    #    "body": {
    #          "data": "...."
    #    }
    # }

    if body.get("data"):

        decoded = decode_body(
            body["data"]
        )


        if mime_type == "text/plain":
            plain_text = decoded


        elif mime_type == "text/html":
            html_text = decoded



    # Case 2:
    # Multipart email
    #
    # payload.parts[]
    #
    # text/plain
    # text/html
    # attachments

    for part in payload.get("parts", []):


        # Ignore files
        #
        # Example:
        # {
        #   "filename": "test.txt"
        # }

        if part.get("filename"):
            continue



        part_type = part.get(
            "mimeType"
        )


        part_body = part.get(
            "body",
            {}
        )


        if part_body.get("data"):

            decoded = decode_body(
                part_body["data"]
            )


            if part_type == "text/plain":

                plain_text = decoded


            elif part_type == "text/html":

                html_text = decoded



        # Nested multipart
        if part.get("parts"):
            nested = extract_body(part)
            if nested and not plain_text:
                plain_text = nested
        


    # Prefer clean text
    if plain_text:
        return plain_text



    # Fallback for HTML-only emails
    if html_text:
        return html_to_text(
            html_text
        )


    return ""