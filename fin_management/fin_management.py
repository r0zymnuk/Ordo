from datetime import datetime
from flask import Blueprint, render_template, request, redirect
from bson.json_util import ObjectId
from .models import currency, Transaction
from db import client
import requests
from decorators import login_required


finances = Blueprint("finances", __name__, url_prefix="/finances", template_folder="templates")


def convert_to_currency(from_curr, to_curr, amount):
    url = f"https://api.exchangerate.host/convert?from={from_curr}&to={to_curr}&amount={amount}"
    r = requests.get(url=url)
    if r.status_code == 200:
        json = r.json()
        if json["success"]:
            return json["result"]
    if r.status_code == 202:
        return "Wrong currency"
    if int(r.status_code) >= 400:
        return "Please try again later"


@finances.get("/management")
@login_required
def get_finances():
    """Returns Array of Savings where User is Owner"""
    transactions = list(client['finances'].find(filter={"owner": ObjectId(request.cookies.get("user_id"))},
                                                sort=[("created_at", -1)],
                                                limit=125))

    income, spending = 0, 0
    for item in transactions:
        if item["type"] == "income":
            income += item["amount"]
        elif item["type"] == "spending":
            spending += item["amount"]

    return render_template(
        "finances.html",
        currencies=currency,
        context={"user": client['user'].find_one({"_id": ObjectId(request.cookies.get("user_id"))})},
        transactions=transactions,
        income=income,
        spending=spending
    )


@finances.post("/add")
@login_required
def add_record():
    amount = float(request.form.get("transactionAmount", 0))
    for cur in currency:
        if cur[0] == request.form.get("currency", "USD"):
            record_currency = cur[0]
            break
    user_currency = client['user'].find_one({"_id": ObjectId(request.cookies.get("user_id"))})["currency"]
    if record_currency != user_currency:
        amount = convert_to_currency(record_currency, user_currency, amount)
    transaction_time = request.form.get("transactionTime", None)

    transaction = Transaction(
        title=request.form.get("title", ""),
        owner=[ObjectId(request.cookies.get("user_id"))],
        amount=amount,
        type=request.form.get("type", "spending")
    )
    if request.form.get("description", False) and request.form.get("description", False) != "":
        transaction.description = request.form.get("description", None)
    if transaction_time and transaction_time != '':
        transaction.transaction_time = datetime.strptime(transaction_time, '%Y-%m-%dT%H:%M')

    created = client["finances"].insert_one(transaction.dict())
    if created.acknowledged:
        return redirect("/finances/management")
    return redirect("/finances/management")


@finances.post("/clear")
@login_required
def clear_budget():
    client["finances"].delete_many({"owner": ObjectId(request.cookies.get("user_id"))})
    return redirect("/finances/management")
