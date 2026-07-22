import os
from dotenv import load_dotenv

from models import Category, Email, ClassifiedEmail, Provider

import json
from openai import OpenAI
from typing import List


from datetime import datetime

"""
тут нам надо получать emails from main, and then LLM will classify

"""

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(
    base_url = "https://api.deepseek.com",
    api_key = API_KEY
)


def build_user_prompt(emails: List[Email]) -> str:
    lines = []
    for email in emails:
        lines.append(
            f"id: {email.id}\n"
            f"sender: {email.sender}\n"
            f"subject: {email.subject}\n"
            f"body_text: {email.body_text[:1000]}\n"
        )


    return "\n".join(lines)

def build_system_prompt() -> str:

    valid_categories = [n.value for n in Category]

    prompt = (
        "You are an email classification assistant for a university student\n"
        f"For each email, assign exactly one category from this list: {valid_categories}\n"
        f"{Category.IMPORTANT.value}: only important notices, such as deadlines, scholarship notices, dormitory chech-in and check-outs\n"
        f"{Category.NORMAL.value}: Things a student needs to finish, but not urgent, such as homeworks and events he may like\n"
        f"{Category.NOT_IMPORTANT.value}: Spam, system notifications, anything not related to a student\n"
        "Add a short summary\n"
        "Return ONLY valid JSON in this exact shape, no extra text: \n"
        "{\n"
            '  "results": [\n'
            '       {"id": "<email id>", "category": "<one of the categories>", "summary": "<short summary>"}'
            "  ]\n"
        "}"
    )

    return prompt


def llm_call(emails: List[Email]) -> List[ClassifiedEmail]:

    try:
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {
                    "role": "system",
                    "content": build_system_prompt()
                },
                {
                    "role": "user",
                    "content": build_user_prompt(emails)
                },
            ],
            response_format={"type": "json_object"},
        )

    except Exception as e:
        raise RuntimeError(f"LLM API call failed: {e}") from e


    try:
        data = json.loads(response.choices[0].message.content)

    except json.JSONDecodeError as e:
        raise RuntimeError("LLM returned invalid JSON") from e


    email_map = {email.id: email for email in emails}

    results = []

    for item in data.get("results", []):

        email = email_map.get(item.get("id"))

        if email is None:
            print(f"Warning: unknown email id {item.get('id')}")
            continue

        try:
            category = Category(item["category"])

        except ValueError:
            print(f"Warning: invalid category {item['category']}")
            continue

        summary = item.get("summary", "")
        results.append(
            ClassifiedEmail(
                email = email,
                category = category,
                summary = item.get("summary")
            )
        )

    return results
if __name__ == "__main__":
    test_emails = [
        Email(
                id="test1",
                provider = Provider.GMAIL,
                sender="boss@company.com",
                subject="Deadline moved up",
                body_text="The project deadline has been moved to this Friday.",
                received_at=datetime.now(),
            ),
            Email(
                id="test2",
                provider = Provider.GMAIL,
                sender="newsletter@shop.com",
                subject="50% off sale",
                body_text="Huge discounts this weekend only!",
                received_at=datetime.now(),
            ),  
    ]
    print(llm_call(test_emails))