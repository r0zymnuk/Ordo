# Ordo
### Video Demo: 
#### Description: Ordo is web based application created to help you organize your life. There you can track your tasks, write notes, track savings and manage your income and spendings.

requirements.txt  This file contains python modules needed to import to make this app work.
db.py   In this file I create connection to my MongoDB cluster.
decorators.py   Here I put path decorator @login_required
### main.py     Here I have an instance of my Flask app and register all blueprints I need to give desired features. This file contains root endpoint "/" of the app.\n
*/__init__.py   Files with this name make folder available to import like python modules. I left these files empty.
*/models.py     In files with this name I put all my Pydantic models 
### /accounts   This folder contains files for */login */register */logout */update */profile endpoints
auth.py     Here are functions I need to authenticate users  
accounts.py  File where I have my accounts blueprint instance and processing all /accounts endpoints

