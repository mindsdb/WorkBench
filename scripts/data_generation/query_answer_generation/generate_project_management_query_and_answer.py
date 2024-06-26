import pandas as pd
import random
import csv
import sys
import os
import numpy as np

project_root = os.path.abspath(os.path.curdir)
sys.path.append(project_root)
random.seed(42)

from src.evals.utils import generate_all_queries_and_answers
from src.data_generation.data_generation_utils import HARDCODED_CURRENT_TIME, get_natural_language_date
from scripts.data_generation.mocked_data.generate_project_management_data import project_management_team_emails

project_tasks = pd.read_csv("data/processed/project_tasks.csv", dtype=str)
emails = project_tasks["assigned_to_email"].unique()
task_names = project_tasks["task_name"].unique()
boards = project_tasks["board"].unique()


def get_random_task_dict():
    task = random.choice(task_names)
    email = random.choice(emails)
    board = random.choice(boards)
    due_date = HARDCODED_CURRENT_TIME.date() + pd.Timedelta(days=random.randint(1, 7))
    natural_language_due_date = get_natural_language_date(due_date)
    return {
        "task_name": task,
        "email": email,
        "board": board,
        "due_date": due_date,
        "natural_language_due_date": natural_language_due_date,
        "name": email.split("@")[0].split(".")[0],
    }


def get_new_task_string(task_name, email, board, due_date):
    return f"""project_management.create_task.func(task_name="{task_name}", board="{board}", assigned_to_email="{email}", due_date="{due_date}", list_name="Backlog")"""


def move_tasks_to_in_review_logic():
    """
    Move all tasks assigned to someone that are in progress to in review.
    """
    email = random.choice(project_management_team_emails)
    name = email.split("@")[0].split(".")[0]

    tasks_in_progress = project_tasks[
        (project_tasks["assigned_to_email"] == email) & (project_tasks["list_name"] == "In Progress")
    ]
    answer = []
    for _, task in tasks_in_progress.iterrows():
        task_id = task["task_id"]
        answer.append(
            f"""project_management.update_task.func(task_id="{task_id}", field="list_name", new_value="In Review")"""
        )
    return {"name": name, "answer": answer}


def add_new_task_logic():
    """
    Add a new task to the backlog and assign it to someone.
    """
    task_dict = get_random_task_dict()
    answer = [
        get_new_task_string(task_dict["task_name"], task_dict["email"], task_dict["board"], task_dict["due_date"])
    ]
    return {"answer": answer, **task_dict}


def move_overdue_tasks_logic():
    """
    Move all overdue tasks that we haven't started on the {board} board to the in-progress
    """
    email = random.choice(project_management_team_emails)
    name = email.split("@")[0].split(".")[0]

    tasks = project_tasks[
        (project_tasks["assigned_to_email"] == email)
        & (project_tasks["list_name"] == "Backlog")
        & (project_tasks["due_date"] < str(HARDCODED_CURRENT_TIME.date()))
    ]
    answer = []
    for _, task in tasks.iterrows():
        task_id = task["task_id"]
        answer.append(
            f"""project_management.update_task.func(task_id="{task_id}", field="list_name", new_value="In Progress")"""
        )
    return {"name": name, "answer": answer}


def move_overdue_in_review_tasks_logic():
    """
    Move any of {name}'s tasks that are In Review to Completed
    """
    email = random.choice(project_management_team_emails)
    name = email.split("@")[0].split(".")[0]
    tasks_in_review = project_tasks[
        (project_tasks["assigned_to_email"] == email) & (project_tasks["list_name"] == "In Review")
    ]
    answer = []
    for _, task in tasks_in_review.iterrows():
        task_id = task["task_id"]
        answer.append(
            f"""project_management.update_task.func(task_id="{task_id}", field="list_name", new_value="Completed")"""
        )
    return {"name": name, "answer": answer}


def reassign_unfinished_tasks_logic():
    """
    Reassign all of {name_1}'s in progress tasks to {name_2}
    """
    email_1 = random.choice(project_management_team_emails)
    email_2 = random.choice(project_management_team_emails)
    while email_1 == email_2:
        email_2 = random.choice(project_management_team_emails)
    name_1 = email_1.split("@")[0].split(".")[0]
    name_2 = email_2.split("@")[0].split(".")[0]
    tasks_in_progress = project_tasks[
        (project_tasks["assigned_to_email"] == email_1) & (project_tasks["list_name"] == "In Progress")
    ]
    answer = []
    for _, task in tasks_in_progress.iterrows():
        task_id = task["task_id"]
        answer.append(
            f"""project_management.update_task.func(task_id="{task_id}", field="assigned_to_email", new_value="{email_2}")"""
        )
    return {"name_1": name_1, "name_2": name_2, "answer": answer}


def move_unfinished_tasks_to_backlog_logic():
    """
    Move all of {name_1}'s unfinished tasks to the backlog
    """
    email_1 = random.choice(project_management_team_emails)
    name_1 = email_1.split("@")[0].split(".")[0]
    tasks_in_progress = project_tasks[
        (project_tasks["assigned_to_email"] == email_1)
        & (project_tasks["list_name"].isin(["In Progress", "Not Started"]))
    ]
    answer = []
    for _, task in tasks_in_progress.iterrows():
        task_id = task["task_id"]
        answer.append(
            f"""project_management.update_task.func(task_id="{task_id}", field="list_name", new_value="Backlog")"""
        )
    return {"name_1": name_1, "answer": answer, "email_1": email_1}


def reassign_overdue_tasks_logic():
    """
    Give all of {name_1}'s overdue tasks to {name_2}
    """
    email_1 = random.choice(project_management_team_emails)
    email_2 = random.choice(project_management_team_emails)
    while email_1 == email_2:
        email_2 = random.choice(project_management_team_emails)
    name_1 = email_1.split("@")[0].split(".")[0]
    name_2 = email_2.split("@")[0].split(".")[0]
    tasks_overdue = project_tasks[
        (project_tasks["assigned_to_email"] == email_1)
        & (project_tasks["due_date"] < str(HARDCODED_CURRENT_TIME.date()))
        & (project_tasks["list_name"] == "Backlog")
    ]
    answer = []
    for _, task in tasks_overdue.iterrows():
        task_id = task["task_id"]
        answer.append(
            f"""project_management.update_task.func(task_id="{task_id}", field="assigned_to_email", new_value="{email_2}")"""
        )
    return {"name_1": name_1, "name_2": name_2, "answer": answer, "email_1": email_1, "email_2": email_2}


def reassign_most_urgent_task_logic():
    """
    Take {name_1}'s most urgent task and reassign it to {name_2}
    """
    email_1 = random.choice(project_management_team_emails)
    email_2 = random.choice(project_management_team_emails)
    while email_1 == email_2:
        email_2 = random.choice(project_management_team_emails)
    name_1 = email_1.split("@")[0].split(".")[0]
    name_2 = email_2.split("@")[0].split(".")[0]
    tasks = project_tasks[(project_tasks["assigned_to_email"] == email_1) & (project_tasks["list_name"] == "Backlog")]
    most_urgent_task = tasks[tasks["due_date"] == tasks["due_date"].min()]
    # If there are multiple tasks with the same due date, try again
    if (len(most_urgent_task) > 1) or (most_urgent_task.empty):
        return reassign_most_urgent_task_logic()
    task_id = most_urgent_task["task_id"].values[0]
    answer = [
        f"""project_management.update_task.func(task_id="{task_id}", field="assigned_to_email", new_value="{email_2}")"""
    ]
    return {"name_1": name_1, "name_2": name_2, "answer": answer, "email_1": email_1, "email_2": email_2}


PROJECT_MANAGEMENT_TEMPLATES = [
    {
        "query": "Move all of {name}'s tasks that are in progress to in review",
        "alternative_queries": [
            "{name} has a bunch of tasks that are in progress. Can you move them to in review?",
            "can you move all of {name}'s tasks that are in progress to in review?",
        ],
        "logic": move_tasks_to_in_review_logic,
    },
    {
        "query": "Add a new task to the {board} backlog called {task_name} and assign it to {name}. It's due on {natural_language_due_date}.",
        "alternative_queries": [
            "can you add a new task called {task_name} to the {board} backlog and assign it to {name}? It's due on {natural_language_due_date}.",
            "I need to add a new task to the {board} backlog called {task_name} and assign it to {name}. It's due on {natural_language_due_date}. Can you do that?",
        ],
        "logic": add_new_task_logic,
    },
    {
        "query": "Move all of {name}'s overdue tasks in the backlog to in progress",
        "alternative_queries": [
            "{name} has a bunch of overdue tasks in the backlog. Can you move them to in progress?",
            "can you move all of {name}'s overdue tasks in the backlog to in progress?",
        ],
        "logic": move_overdue_tasks_logic,
    },
    {
        "query": "Move any of {name}'s tasks that are in review to completed",
        "alternative_queries": [
            "I've finished reviewing all of {name}'s tasks. Can you move all the ones that are in review to completed?",
            "can you move any of {name}'s tasks that are in review to completed?",
        ],
        "logic": move_overdue_in_review_tasks_logic,
    },
    {
        "query": """{name_1} is sick so reassign their in progress tasks to {name_2}.""",
        "alternative_queries": [
            "can you reassign all of {name_1}'s in progress tasks to {name_2}?",
            "I need to reassign all of {name_1}'s in progress tasks to {name_2}. Can you do that?",
        ],
        "logic": reassign_unfinished_tasks_logic,
    },
    {
        "query": """{name_1} is on vacation now so move all their unfinished tasks to the backlog.""",
        "alternative_queries": [
            "can you move all of {name_1}'s unfinished tasks to the backlog?",
            "I need to move all of {name_1}'s unfinished tasks to the backlog. Can you do that?",
        ],
        "logic": move_unfinished_tasks_to_backlog_logic,
    },
    {
        "query": """Give all the overdue tasks that {name_1} hasn't started to {name_2}.""",
        "alternative_queries": [
            "{name_2} has some free time so can you give them all of {name_1}'s overdue tasks that they haven't started?",
            "can you give all of {name_1}'s overdue tasks that they haven't started to {name_2}?",
        ],
        "logic": reassign_overdue_tasks_logic,
    },
    {
        "query": """Take {name_1}'s most urgent task and reassign it to {name_2}.""",
        "alternative_queries": [
            "can you take {name_1}'s most urgent task and reassign it to {name_2}?",
            "I need to take {name_1}'s most urgent task and reassign it to {name_2}. Can you do that?",
        ],
        "logic": reassign_most_urgent_task_logic,
    },
]
for d in PROJECT_MANAGEMENT_TEMPLATES:
    d["domains"] = ["project_management"]


def generate_query_and_answer():
    np.random.seed(42)
    random.seed(42)
    max_queries_per_template = 10  # Limit the number of queries per template
    generated_queries_and_answers = generate_all_queries_and_answers(
        PROJECT_MANAGEMENT_TEMPLATES, max_queries_per_template
    )
    df = pd.DataFrame(generated_queries_and_answers)
    df.to_csv(
        "data/processed/queries_and_answers/project_management_queries_and_answers.csv",
        index=False,
        quoting=csv.QUOTE_ALL,
    )


if __name__ == "__main__":
    generate_query_and_answer()
