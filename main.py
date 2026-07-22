from auth.gmail_auth import get_gmail_credentials
from googleapiclient.discovery import build

from fetcher import get_new_emails
from classifier import llm_call


def main():

    # 1. Get Gmail credentials
    creds = get_gmail_credentials()

    # 2. Create Gmail API service
    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    # 3. Fetch emails
    emails = get_new_emails(
        service,
        max_results=10
    )

    print(f"Fetched {len(emails)} emails\n")


    # Debug: посмотреть что пришло
    for email in emails:
        print("SUBJECT:", email.subject)
        print("FROM:", email.sender)
        print("BODY LENGTH:", len(email.body_text))
        print("-" * 40)


    # 4. Classify with DeepSeek
    classified = llm_call(emails)


    # 5. Print results
    print("\nCLASSIFICATION RESULTS\n")

    for item in classified:
        print("=" * 50)
        print("Subject:", item.email.subject)
        print("Sender:", item.email.sender)
        print("Category:", item.category.value)
        print("Summary:", item.summary)


if __name__ == "__main__":
    main()