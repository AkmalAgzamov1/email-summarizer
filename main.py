from googleapiclient.discovery import build

from auth.gmail_auth import get_gmail_credentials
from fetcher import get_new_emails



def main():

    creds = get_gmail_credentials()


    service = build(
        "gmail",
        "v1",
        credentials=creds
    )


    emails = get_new_emails(
        service,
        max_results=5
    )


    print(
        f"\nReceived {len(emails)} emails\n"
    )


    for index, email in enumerate(emails, start=1):

        print("=" * 60)
        print(f"EMAIL #{index}")
        print("=" * 60)

        print(
            f"From: {email.sender}"
        )

        print(
            f"Subject: {email.subject}"
        )

        print(
            f"Date: {email.received_at}"
        )

        print("\nBody:")

        if email.body_text:
            print(
                email.body_text[:500]
            )
        else:
            print(
                "[EMPTY BODY]"
            )

        print()



if __name__ == "__main__":
    main()