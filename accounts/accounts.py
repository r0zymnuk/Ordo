from flask import Blueprint, session, render_template, request, redirect, make_response
from bson.json_util import ObjectId
from .auth import authenticate_user, get_password_hash, check_username, check_if_email, generate_username
from db import client
from .models import UserInDB
from fin_management.fin_management import convert_to_currency
from fin_management.models import currency
from decorators import login_required

route = Blueprint("accounts", __name__, url_prefix="/accounts", template_folder="templates")


@route.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", context={})
    if request.method == "POST":
        if not request.form.get("email") or not request.form.get("password"):
            return render_template("login.html", error="All fields required")

        user = authenticate_user(request.form.get("email"), request.form.get("password"))
        print(user)
        if not user:
            return render_template("login.html", error="Invalid credentials")

        resp = make_response(redirect("/"))
        resp.set_cookie("user_id", str(user.id))
        return resp


@route.get("/logout")
@login_required
def logout():
    resp = make_response(redirect("/"))
    resp.delete_cookie("user_id")
    # Redirect user to login form
    return resp


@route.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        if not request.form.get("email") or not request.form.get("password") or not request.form.get("passwordConfirm"):
            return render_template("register.html", error="All fields required")
        if request.form.get("password") != request.form.get("passwordConfirm"):
            return render_template("register.html", error="Passwords do not match")
        is_email = check_if_email(request.form.get("email"))

        valid_username = check_username(request.form.get("email"))
        if valid_username == "email":
            return render_template("register.html", error="Email is already taken")
        if valid_username == "username":
            return render_template("register.html", error="Username is already taken")

        if is_email:
            username = generate_username()
            email = request.form.get("email")
        else:
            username = request.form.get("email")
            email = None

        if request.form.get("name"):
            full_name = request.form.get("name")
            name = full_name.split(" ")[0]
        else:
            full_name = None
            name = None

        created_user = UserInDB(username=username, email=email, hashed=get_password_hash(request.form.get("password")),
                                full_name=full_name, name=name, currency="USD", id=None)
        inserted = client["user"].insert_one(created_user.dict())
        if inserted.acknowledged:
            resp = make_response(redirect("/"))
            resp.set_cookie("user_id", str(inserted.inserted_id))
            return resp

        return render_template("register.html", error="Error occurred")


@route.get("/<userId>/delete")
@login_required
def delete_account(userId):
    if userId != session.get("user_id", ' '):
        return redirect("/")
    deleted = client["user"].find_one_and_delete({"_id": ObjectId(userId)})
    if deleted:
        session.clear()
    return redirect("/")


@route.route("/profile", methods=["GET", "POST"])
@login_required
def get_profile():
    user = client["user"].find_one({"_id": ObjectId(request.cookies.get("user_id"))})
    message = ""
    if request.method == "GET":
        pass
    if request.method == "POST":
        field_updated = []
        if request.form.get("email", False) and request.form.get("email", False) != "":
            if client["user"].count_documents({"email": request.form.get("email", False)}) == 0:
                client["user"].find_one_and_update({"_id": ObjectId(request.cookies.get("user_id"))},
                                                   {"$set": {"email": request.form.get("email", False)}})
                field_updated.append("email")
            else:
                return render_template(
                    "profile.html",
                    context={"user": user},
                    user=user,
                    message="Email is already taken",
                    currencies=currency
                )

        if request.form.get("username", False) != "":
            if client["user"].count_documents({"username": request.form.get("username", False)}) == 0:
                updated = client["user"].find_one_and_update({"_id": ObjectId(request.cookies.get("user_id"))},
                                                             {"$set": {
                                                                 "username": request.form.get("username", False)}})
                if updated is not None:
                    field_updated.append("username")

        if request.form.get("last_name", False) != "":
            name = client["user"].find_one({"_id": ObjectId(request.cookies.get("user_id"))}).get("name", "")
            updated = client["user"].find_one_and_update({"_id": ObjectId(request.cookies.get("user_id"))},
                                                         {"$set": {
                                                             "full_name": name + ' ' + request.form.get("last_name",
                                                                                                        ""),
                                                             "last_name": request.form.get("last_name", "")}})
            if updated is not None:
                field_updated.append("full name, last name")

        if request.form.get("name", False) != "":
            updated = client["user"].find_one_and_update({"_id": ObjectId(request.cookies.get("user_id"))},
                                                         {"$set": {"name": request.form.get("name", False)}})
            if updated is not None:
                field_updated.append("name")
        if request.form.get("password", False) != "":
            if not request.form.get("passwordConfirm", False) and request.form.get("passwordConfirm", False) != "":
                return render_template(
                    "profile.html",
                    context={"user": user},
                    user=user,
                    message="Confirmation password is needed",
                    currencies=currency
                )
            if request.form.get("passwordConfirm", False) != request.form.get("password", False):
                return render_template(
                    "profile.html",
                    context={"user": user},
                    user=user,
                    message="Passwords do not match",
                    currencies=currency
                )
            updated = client["user"].find_one_and_update(
                {"_id": ObjectId(request.cookies.get("user_id"))},
                {"$set": {"hashed": get_password_hash(request.form.get("password"))}}
            )
            if updated is not None:
                field_updated.append("password")
        if request.form.get("currency") != user["currency"]:
            finances = client["finances"].find(
                {"owner": ObjectId(request.cookies.get("user_id"))}, {"_id": 1, "amount": 1}
            )
            for record in finances:
                new_amount = convert_to_currency(user["currency"], request.form.get("currency"), record["amount"])
                if isinstance(new_amount, (int, float)):
                    client["finances"].find_one_and_update({"_id": record["_id"]}, {"$set": {"amount": new_amount}})
                else:
                    return {"Error": "Please try again later"}
            client["user"].find_one_and_update(
                {"_id": ObjectId(request.cookies.get("user_id"))}, {"$set": {"currency": request.form.get("currency")}}
            )
            field_updated.append("currency")
        user = client["user"].find_one({"_id": ObjectId(request.cookies.get("user_id"))})

        if len(field_updated) > 0:
            message = "Updated fields: " + ", ".join(field_updated)
        else:
            message = "No fields were updated"
    return render_template(
        "profile.html",
        profile=True,
        context={"user": user},
        user=user,
        message=message,
        currencies=currency
    )
