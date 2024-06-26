import pandas as pd
import random
import csv
import sys
import os
import numpy as np

project_root = os.path.abspath(os.path.curdir)
sys.path.append(project_root)

from src.evals.utils import generate_all_queries_and_answers
from src.data_generation.data_generation_utils import HARDCODED_CURRENT_TIME

random.seed(42)


emails_data = pd.read_csv("data/processed/emails.csv", dtype=str)
email_ids = list(emails_data["email_id"].unique())
subjects = list(emails_data["subject"].unique())
senders = list(emails_data["sender/recipient"].unique())
dates = list(emails_data["sent_datetime"].str.split(" ").str[0].unique())
bodies = list(emails_data["body"].unique())
datetimes = list(emails_data["sent_datetime"].str.split(" ").str[0].unique())


def delete_last_email_logic():
    sender = random.choice(senders)
    name = sender.split("@")[0].split(".")[0]
    last_email_id = emails_data[emails_data["sender/recipient"] == sender].iloc[-1]["email_id"]
    answer = [f"""email.delete_email.func(email_id="{last_email_id}")"""]
    return {
        "name": name,
        "last_email_id": last_email_id,
        "answer": answer,
    }


def delete_last_days_emails_logic():
    sender = random.choice(senders)
    name = sender.split("@")[0].split(".")[0]
    days = random.randint(2, 7)
    last_days_emails = emails_data[
        emails_data["sent_datetime"] >= str(HARDCODED_CURRENT_TIME - pd.Timedelta(days=days))
    ]
    last_days_emails = last_days_emails[last_days_emails["sender/recipient"] == sender]
    last_days_emails = last_days_emails["email_id"].tolist()
    answer = []
    for email_id in last_days_emails:
        answer.append(f"""email.delete_email.func(email_id="{email_id}")""")
    return {
        "name": name,
        "days": days,
        "answer": answer,
    }


def forward_recent_email_from_sender_logic():
    sender_email = random.choice(senders)
    sender_name = sender_email.split("@")[0].split(".")[0]
    last_email_id = emails_data[emails_data["sender/recipient"] == sender_email].iloc[-1]["email_id"]
    recipient_email = random.choice(senders)
    while recipient_email == sender_email:
        recipient_email = random.choice(senders)
    recipient_name = recipient_email.split("@")[0].split(".")[0]
    answer = [f"""email.forward_email.func(email_id="{last_email_id}", recipient="{recipient_email}")"""]
    return {
        "sender_name": sender_name,
        "recipient_name": recipient_name,
        "last_email_id": last_email_id,
        "recipient_email": recipient_email,
        "answer": answer,
    }


def forward_recent_email_about_topic_logic():
    email_subject = random.choice(subjects)
    email = emails_data[emails_data["subject"] == email_subject].iloc[-1]
    recipient_email = random.choice(senders)
    while recipient_email == email["sender/recipient"]:
        recipient_email = random.choice(senders)
    recipient_name = recipient_email.split("@")[0].split(".")[0]
    answer = [f"""email.forward_email.func(email_id="{email['email_id']}", recipient="{recipient_email}")"""]
    return {
        "recipient_name": recipient_name,
        "recipient_email": recipient_email,
        "subject": email_subject,
        "answer": answer,
    }


def forward_recent_email_about_topic_to_multiple_logic():
    email_subject = random.choice(subjects)
    email = emails_data[emails_data["subject"] == email_subject].iloc[-1]
    recipient_emails = random.sample([e for e in senders if e != email["sender/recipient"]], k=2)
    recipient_names = [email.split("@")[0].split(".")[0] for email in recipient_emails]
    recipient_name1, recipient_name2 = recipient_names
    answer = []
    for recipient_email in recipient_emails:
        answer.append(f"""email.forward_email.func(email_id="{email["email_id"]}", recipient="{recipient_email}")""")
    return {
        "recipient_name1": recipient_name1,
        "recipient_name2": recipient_name2,
        "subject": email_subject,
        "answer": answer,
    }


def reply_to_email_logic():
    emails_data["name"] = emails_data["sender/recipient"].str.split("@").str[0].str.split(".").str[0]
    email_subject = random.choice(subjects)
    name = random.choice(senders).split("@")[0].split(".")[0]
    selected_email_data = emails_data[(emails_data["subject"] == email_subject) & (emails_data["name"] == name)]

    # Keep looping until we find a subject and name that exists in the emails data and isn't a meeting reschedule
    while (len(selected_email_data) == 0) or (email_subject == "Meeting Rescheduled"):
        email_subject = random.choice(subjects)
        name = random.choice(senders).split("@")[0].split(".")[0]
        selected_email_data = emails_data[(emails_data["subject"] == email_subject) & (emails_data["name"] == name)]
    email_id = selected_email_data.sort_values("sent_datetime", ascending=False).iloc[0]["email_id"]

    del emails_data["name"]
    answer = [
        f"""email.reply_email.func(email_id="{email_id}", body="Thanks for the update - I will get back to you tomorrow.")"""
    ]
    return {
        "name": name,
        "email_id": email_id,
        "subject": email_subject,
        "answer": answer,
    }


def reply_to_latest_email_logic():
    sender_email = random.choice(senders)
    sender_name = sender_email.split("@")[0].split(".")[0]
    last_email_id = emails_data[emails_data["sender/recipient"] == sender_email].iloc[-1]["email_id"]
    answer = [f"""email.reply_email.func(email_id="{last_email_id}", body="Got it, thank you!")"""]
    return {
        "sender_name": sender_name,
        "answer": answer,
    }


def replace_name(body, name):
    """Replaced the first occurance of "Sam" with the name of the email recipient. And replace the sign off with "Sam"."""
    body = body.split("\\n")
    body[-1] = f"\\nSam"
    body = "\\n".join(body)
    return body.replace("Sam", name, 1)


def send_email_logic():
    index = random.randint(0, len(subjects) - 1)
    subject = subjects[index]
    recipient_email = random.choice(senders)
    name = recipient_email.split("@")[0].split(".")[0]
    body = bodies[index]
    body = replace_name(body, name)
    answer = [f"""email.send_email.func(recipient="{recipient_email}", subject="{subject}", body="{body}")"""]
    return {
        "body": body,
        "subject": subject,
        "name": name,
        "recipient_email": recipient_email,
        "answer": answer,
    }


def forward_last_weeks_email_logic():
    last_week_email = emails_data[
        (emails_data["sent_datetime"] >= "2023-11-20") & (emails_data["sent_datetime"] <= "2023-11-26")
    ]
    email = random.choice(last_week_email["sender/recipient"].unique())
    last_week_email = last_week_email[last_week_email["sender/recipient"] == email]
    subject = random.choice(last_week_email["subject"].unique())
    last_week_email = last_week_email[last_week_email["subject"] == subject]
    recipient_email = random.choice(senders)
    while recipient_email == email:
        recipient_email = random.choice(senders)
    recipient_name = recipient_email.split("@")[0].split(".")[0]
    answer = []
    for email_id in last_week_email["email_id"]:
        answer.append(f"""email.forward_email.func(email_id="{email_id}", recipient="{recipient_email}")""")
    return {
        "name": email.split("@")[0].split(".")[0],
        "recipient_name": recipient_name,
        "recipient_email": recipient_email,
        "subject": subject,
        "answer": answer,
    }


EMAIL_TEMPLATES = [
    {
        "query": "Delete my last email from {name}",
        "alternative_queries": [
            "I need to delete my last email from {name}. Can you do that?",
            "{name} just sent me an email that I need to delete. Can you get rid of of the most recent email they sent me?",
        ],
        "logic": delete_last_email_logic,
    },
    {
        "query": "Delete all my emails from {name} from the last {days} days",
        "alternative_queries": [
            "I need to get rid of all my emails from {name} from the last {days} days. Can you do delete them?",
            "All my emails from {name} from the last {days} days need to be deleted. Can you do that?",
        ],
        "logic": delete_last_days_emails_logic,
    },
    {
        "query": "Send an email to {name} saying '{body}' and title it '{subject}'",
        "alternative_queries": [
            "please send an email to {name} saying '{body}' and title it '{subject}'",
            "I need to send an email to {name} saying '{body}' and title it '{subject}'. Can you do that?",
        ],
        "logic": send_email_logic,
    },
    {
        "query": "Reply to {name}'s last email about '{subject}' with 'Thanks for the update - I will get back to you tomorrow.'",
        "alternative_queries": [
            "can you reply to {name}'s last email about '{subject}' with 'Thanks for the update - I will get back to you tomorrow.'",
            "I need to get back to {name}'s last email about '{subject}' with 'Thanks for the update - I will get back to you tomorrow. Can you send the reply for me?",
        ],
        "logic": reply_to_email_logic,
    },
    {
        "query": "Forward all the emails from {name} last week about '{subject}' to {recipient_name}",
        "alternative_queries": [
            "{recipient_name} needs all the emails from {name} last week about '{subject}'. Can you forward them?",
            "can you forward all the emails from {name} last week about '{subject}' to {recipient_name}",
        ],
        "logic": forward_last_weeks_email_logic,
    },
    {
        "query": "Forward the latest email about '{subject}' to {recipient_name}",
        "alternative_queries": [
            "{recipient_name} needs the latest email about '{subject}'. Can you forward it?",
            "can you forward the latest email about '{subject}' to {recipient_name}",
        ],
        "logic": forward_recent_email_about_topic_logic,
    },
    {
        "query": "Forward my most recent email from {sender_name} to {recipient_name}",
        "alternative_queries": [
            "{recipient_name} needs my most recent email from {sender_name}. Can you forward it?",
            "can you forward my most recent email from {sender_name} to {recipient_name}",
        ],
        "logic": forward_recent_email_from_sender_logic,
    },
    {
        "query": "Forward the last email about '{subject}' to {recipient_name1} and {recipient_name2}",
        "alternative_queries": [
            "{recipient_name1} and {recipient_name2} need the last email about '{subject}'. Can you forward it?",
            "can you forward the last email about '{subject}' to {recipient_name1} and {recipient_name2}",
        ],
        "logic": forward_recent_email_about_topic_to_multiple_logic,
    },
    {
        "query": "Reply to the latest email from {sender_name} with 'Got it, thank you!'",
        "alternative_queries": [
            "can you reply to the latest email from {sender_name} with 'Got it, thank you!'",
            "I need to reply to the latest email from {sender_name} with 'Got it, thank you!'. Can you do that?",
        ],
        "logic": reply_to_latest_email_logic,
    },
]
for d in EMAIL_TEMPLATES:
    d["domains"] = ["email"]


def generate_query_and_answer():
    np.random.seed(42)
    random.seed(42)
    # Generate a limited number of unique multi-action queries and answers
    generated_queries_and_answers = []
    max_queries_per_template = 10  # Limit the number of queries per template
    generated_queries_and_answers = generate_all_queries_and_answers(EMAIL_TEMPLATES, max_queries_per_template)
    df = pd.DataFrame(generated_queries_and_answers)
    df.to_csv(
        "data/processed/queries_and_answers/email_queries_and_answers.csv",
        index=False,
        quoting=csv.QUOTE_ALL,
    )


if __name__ == "__main__":
    generate_query_and_answer()
