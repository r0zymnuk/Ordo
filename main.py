from flask import Flask, render_template, request, redirect
from flask_session import Session
import datetime
from db import client
from bson import ObjectId
from tasks.tasks import tasks
from accounts.accounts import route as accounts
from notes.notes import router as notes
from savings.savings import savings
from fin_management.fin_management import finances


app = Flask(__name__)
app.permanent_session_lifetime = datetime.timedelta(days=365)
app.secret_key = "LvGsXmGRwdO4WQ0y"
app.register_blueprint(tasks)
app.register_blueprint(accounts)
app.register_blueprint(notes)
app.register_blueprint(savings)
app.register_blueprint(finances)
# app.config.from_object(__name__)
Session(app)


@app.route("/")
def root():
    context = {}
    if request.cookies.get("user_id") is not None and len(request.cookies.get("user_id")) > 12:
        user_context = {}
        user = client["user"].find_one({"_id": ObjectId(request.cookies.get("user_id"))})
        if user is None:
            return redirect("/accounts/logout")
        user_context["id"] = request.cookies.get("user_id")
        user_context["name"] = user.get("name", user.get("full_name", user["username"]))
        context["user"] = user_context
    return render_template(
        "main.html",
        landing=True,
        context=context
    )
