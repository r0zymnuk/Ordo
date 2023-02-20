from datetime import datetime

import markdown
from bson.json_util import ObjectId
from flask import Blueprint, render_template, request, redirect

from accounts.models import ResponseUser
from db import client
from decorators import login_required
from .models import ToDo

tasks = Blueprint("tasks", __name__, url_prefix="/tasks", template_folder="templates")


@tasks.route("/")
@login_required
def get_tasks():
    todo = list(client['todo'].find({'owner': ObjectId(request.cookies.get("user_id"))},
                                    sort=[('created_at', -1)]))
    for task in todo:
        task['description'] = markdown.markdown(task['description'])
        task["id"] = str(task["_id"])
        del task["_id"]
        task["owner"] = str(task["owner"])
    user = ResponseUser(**client['user'].find_one({'_id': ObjectId(request.cookies.get("user_id"))},
                                                  {"hashed": 0, "disabled": 0}))

    return render_template(
        "tasks.html",
        context={
            "user": user
        },
        tasks=todo
    )


@tasks.route("/<taskId>", methods=["POST"])
@login_required
def update_task_status(taskId):
    status = request.args.get("status", "Not completed")
    userId = request.cookies.get("user_id")
    if status == "Not completed":
        return redirect("/tasks/")

    task = client["todo"].find_one({"_id": ObjectId(taskId), "owner": ObjectId(userId)})
    if not task:
        return redirect("/tasks/")

    updated = client["todo"].update_one({"_id": ObjectId(taskId), "owner": ObjectId(userId)},
                                        {"$set": {"status": status.capitalize()}, "$currentDate": {"completed": True}})
    if updated.acknowledged and updated.modified_count == 1:
        return redirect("/tasks/")
    return redirect("/tasks/")


@tasks.route("/create", methods=["POST"])
@login_required
def create_task():
    userId = request.cookies.get("user_id")
    if not request.form.get("task", None):
        return redirect("/tasks/")

    new_task = ToDo(task=request.form.get("task"),
                    description=request.form.get("description", ""),
                    created_at=datetime.now(),
                    owner=str(ObjectId(userId)))

    due_to = request.form.get("dueTo", None)
    print(due_to)
    if due_to and due_to != '':
        new_task.due_to = datetime.strptime(due_to, '%Y-%m-%dT%H:%M')

    new_task = new_task.dict()
    del new_task["id"]
    inserted = client["todo"].insert_one(new_task)
    if inserted.acknowledged:
        return redirect("/tasks/")

    return redirect("/tasks/")


@tasks.route("/<taskId>/delete", methods=["POST"])
@login_required
def delete_task(taskId):
    deleted = client["todo"].find_one_and_delete(
        {"_id": ObjectId(taskId), "owner": ObjectId(request.cookies.get("user_id"))}
    )
    if deleted:
        return redirect("/tasks/")
