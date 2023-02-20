from bson import ObjectId
from flask import Blueprint, request, redirect, render_template
from .models import CreateNote, Note
from db import client
import markdown
from decorators import login_required

router = Blueprint("notes", __name__, url_prefix="/notes", template_folder="templates")


@router.route("/", methods=["GET"])
@login_required
def get_notes():
    user_id = request.cookies.get("user_id")
    notes_filter = {"owner": ObjectId(user_id)}

    notes = list(client["ordo"].find(filter=notes_filter, sort=[("created_at", -1), ("updated_at", -1)]))
    for note in notes:
        note['content'] = markdown.markdown(note['content'])
    return render_template(
        "notes.html",
        notes=notes,
        context={"user": client["user"].find_one({"_id": ObjectId(request.cookies.get("user_id"))})}

    )


@router.post("/create")
@login_required
def create_note():
    note = CreateNote(
        content=request.form.get("note"),
        owner=[ObjectId(request.cookies.get("user_id"))]
    )
    note = Note(**note.dict()).dict()
    posted = client["ordo"].insert_one(note)

    if posted.acknowledged:
        return redirect("/notes/")
    return False


@router.route("/<noteId>/update", methods=["GET", "POST"])
@login_required
def update_note(noteId):
    if request.method == "GET":
        note = client["ordo"].find_one({"_id": ObjectId(noteId), "owner": ObjectId(request.cookies.get("user_id"))})
        if note is None:
            return redirect("/notes/")
        return render_template(
            "note_update.html",
            notes=True,
            context={"user": client["user"].find_one({"_id": ObjectId(request.cookies.get("user_id"))})},
            note=note
        )
    if request.method == "POST":
        updated = client["ordo"].find_one_and_update(
            {"_id": ObjectId(noteId), "owner": ObjectId(request.cookies.get("user_id"))},
            {"$set": {"content": request.form.get("note")}, "$currentDate": {"updated_at": True}}
        )
        if updated is not None:
            return redirect("/notes/")
        return redirect("/notes/")


@router.get("/<noteId>/delete")
@login_required
def delete_note(noteId):
    client["ordo"].find_one_and_delete({"_id": ObjectId(noteId), "owner": ObjectId(request.cookies.get("user_id"))})
    return redirect("/notes/")
