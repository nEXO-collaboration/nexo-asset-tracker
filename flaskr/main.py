from flask import Blueprint, redirect, render_template, request, session, url_for
# from asset_tracker_restapi import asset_tracker_restapi


bp = Blueprint("main", __name__)


@bp.route("/", methods=['GET', 'POST'])
def index():
    jira_username = session.get("jira_username")
    if jira_username is None:
        return redirect(url_for("auth.login"))
    else:
        print("Username :", jira_username)

    return render_template('main.html')


@bp.route("/action", methods=['GET', 'POST'])
def action():
    if request.method == "POST":

        if request.form['submit'] == 'Perform Action':
            action_id = 0
            asset_id = request.form["asset_id"]
            asset_action = request.form["asset_action"]
            if 'action_id' in request.form:
                if request.form["action_id"] != '':
                    action_id = int(request.form["action_id"])
            return redirect(url_for("asset.asset_action", asset_id=asset_id, asset_action=asset_action, action_id=action_id))

        elif request.form['submit'] == 'Find Asset':
            asset_id = request.form["asset_id"]
            return redirect(url_for("asset.asset", asset_id=asset_id))

    return render_template('main.html')


@bp.route("/search", methods=['GET','POST'])
def search():
    # Probably should add in search functionality one of these days I suppose.
    return render_template('main.html')
