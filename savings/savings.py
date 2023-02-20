from flask import Blueprint, render_template, request, redirect
from bson.json_util import ObjectId
from .models import Saving, Currency, Finance
from db import client
from fin_management.models import currency
from decorators import login_required

savings = Blueprint("savings", __name__, url_prefix="/savings", template_folder="templates")


@savings.get("/")
@login_required
def get_savings():
    """Returns Array of Savings where User is Owner"""
    filter_savings = {"owner": ObjectId(request.cookies.get("user_id"))}

    return render_template(
        "savings.html",
        currencies=currency,
        context={"user": client['user'].find_one({"_id": ObjectId(request.cookies.get("user_id"))})},
        savings=client['savings'].find(filter=filter_savings, sort=[("created_at", -1), ("due_to", -1), ("completed", -1)])
    )


@savings.post("/create")
@login_required
def create_saving():
    for cur in currency:
        if cur[0] == request.form.get("currency", "USD"):
            saving_currency = cur
            break
    saving = Saving(title=request.form.get("title"),
                    owner=[ObjectId(request.cookies.get("user_id"))],
                    finance=Finance(target=float(request.form.get("target")),
                                    currency=Currency(name=saving_currency[1], code=saving_currency[0])))
    if request.form.get("description", False) and request.form.get("description", False) != "":
        saving.description = request.form.get("description", None)

    created = client["savings"].insert_one(saving.dict())
    if created.acknowledged:
        return redirect("/savings/")
    return redirect("/savings/")


@savings.post("/<savingId>/delete")
@login_required
def delete_saving(savingId):
    client['savings'].find_one_and_delete(
        {"_id": ObjectId(savingId), "owner": ObjectId(request.cookies.get("user_id"))}
    )
    return redirect("/savings/")


@savings.post("/<savingId>/add")
@login_required
def add_money(savingId):
    update_values = {
            "$inc": {
                "finance.now": int(request.form.get("addAmount", 0))
            }
        }
    current = client['savings'].find_one({'_id': ObjectId(savingId), 'owner': ObjectId(request.cookies.get("user_id"))})
    if (current["finance"]["now"] + int(request.form.get("addAmount", 0))) > current["finance"]["target"]:
        update_values["$currentDate"] = {
            "closed_at": True
        }
    client['savings'].find_one_and_update(
        {'_id': ObjectId(savingId), 'owner': ObjectId(request.cookies.get("user_id"))},
        update=update_values
    )
    return redirect("/savings/")
