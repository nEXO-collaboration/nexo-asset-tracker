from flask import Blueprint, g, redirect, render_template, request, url_for, current_app, session, send_from_directory
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from datetime import datetime
import base64
import os
from io import BytesIO
from asset_tracker_restapi import asset_tracker_restapi
import pprint

bp = Blueprint("asset", __name__)
UPLOAD_FOLDER = './uploads/'  # ! Folder where files are temporarily downloaded from JIRA for the user to download in their browser


@bp.context_processor
def utility_processor():
    asset_api = asset_tracker_restapi(username=session["jira_username"], password=session["jira_password"])
    #  Helper function to be able to get the history of an objects attribute inside of a template

    def attribute_history(asset_id, attribute):
        return asset_api.get_object_attribute_history(asset_id, attribute)
    return dict(attribute_history=attribute_history)


@bp.route("/asset/<string:asset_id>")
def asset(asset_id):
    """Show a single asset, everything about it"""
    asset_api = asset_tracker_restapi(username=session["jira_username"], password=session["jira_password"])
    asset_data = asset_api.get_asset_by_id(asset_id)
    if asset_data == 0:
        print("Item Not found")
        return render_template('main.html')
    # !!A lot of what is below should be moved back into the asset tracker api
    object_type_id = asset_api.get_asset_object_type_by_id(asset_id)
    asset_attribute_list = asset_api.get_object_type_attributes(object_type_id)

    # Search for any attributes that may exist for the asset but that are not currently a part of the asset entry
    # This can happen when a new attribute it added to the object but no value was set in JIRA.
    for asset_attribute in asset_attribute_list:  # Iterate over all attributes
        if asset_attribute['hidden'] is False and asset_attribute['editable'] is True:  # disgard any that are hidden or not editable
            my_attribute_exists = False
            for my_asset in asset_data:  # loop over actual asset data and see if the attribute field exists
                if my_asset['id'] == asset_attribute['id']:
                    my_attribute_exists = True
                    break
            if my_attribute_exists is False:
                asset_data.append(asset_attribute)  # if we find an attribute that doesn't exist then go ahead and pop it on the list

    for my_asset in asset_data:
        if my_asset['field_type'] == 'Select':
            # The following matches up the asset_id with the id of the attribute from the asset_attribute_list to pull out options for a select field type
            my_asset.update({'options': attrib_field['options'] for attrib_field in asset_attribute_list if attrib_field['id'] == my_asset['id']})

    asset_files = asset_api.get_asset_attachments(asset_id)
    tickets = asset_api.get_asset_connected_tickets(asset_id)

    asset_name = asset_api.get_asset_field_from_json_by_name('Name', asset_data)
    return render_template('asset.html', asset_name=asset_name, object_id=asset_id, object_type_id=object_type_id, asset_data=asset_data, asset_files=asset_files, tickets=tickets)


@bp.route("/asset_update", methods=["POST"])
def asset_update():
    # Called from a form when updating an asset, just passes the form info back to the asset tracker api.
    asset_api = asset_tracker_restapi(username=session["jira_username"], password=session["jira_password"])
    asset_api.get_asset_object_type_by_id(request.form['object_id'])
    asset_id = asset_api.update_asset_from_dict(request.form)
    return redirect(url_for("asset.asset", asset_id=asset_id))


@bp.route("/asset_new")
def asset_new():
    #  This uses schema_id to get a list of available object schema's underneath the primary schema
    #  this is also used when creating a new asset
    schema_id = 1  # !!Currently this is set to the first schema, we should move this setting elsewhere
    asset_api = asset_tracker_restapi(username=session["jira_username"], password=session["jira_password"])
    category_list = asset_api.get_object_types_for_schema(schema_id)
    return render_template('newasset_category_selection.html', category_list=category_list)


@bp.route("/new_selected_category", methods=["POST"])
def new_selected_category():
    # Uses the asset tracker api to get all attributes associated with an object scema, typically this is called when
    # creating a new asset
    asset_api = asset_tracker_restapi(username=session["jira_username"], password=session["jira_password"])
    asset_attribute_list = asset_api.get_object_type_attributes(request.form["asset_category_id"])
    return render_template('new_asset.html', asset_attribute_list=asset_attribute_list, category_id=request.form["asset_category_id"])


@bp.route("/asset_create", methods=["POST"])
def asset_create():
    # Creates a new asset from a form, feeds the form dict into the asset tracker API which handles everything
    asset_api = asset_tracker_restapi(username=session["jira_username"], password=session["jira_password"])
    asset_id = asset_api.add_asset_from_dict(request.form)
    if request.form['comment']:  # Check if there was a comment added to the file, if not just put one saying who uploaded it
        comment = request.form['comment']
    else:
        comment = "Uploaded by %s" % session["jira_username"]
    if 'asset_image' in request.files:
        asset_api.upload_file_to_object(asset_id, request.files['asset_image'], comment)
    return redirect(url_for("asset.asset", asset_id=asset_id))


@bp.route("/asset_download_file", methods=["POST"])
def asset_download_file():
    # Download a file from an asset, this pulls it down from JIRA locally to the FLASK system and then
    # sends it to the users browser
#     # ! Need to figure out how to delete file afterwards... maybe cron.. maybe something better..
    asset_api = asset_tracker_restapi(username=session["jira_username"], password=session["jira_password"])
    asset_id = request.form['object_id']
    my_filename = secure_filename(asset_id + '_' + request.form['filename'])
    my_file = asset_api.get_file_from_object(asset_id, request.form['file_url'])
    open(os.path.abspath(UPLOAD_FOLDER+my_filename), 'wb').write(my_file.content)
    return send_from_directory(os.path.abspath(UPLOAD_FOLDER), my_filename, as_attachment=True)


@bp.route("/asset_add_file", methods=["POST"])
def asset_add_file():
    # Adds a file with a comment to an existing asset
    asset_api = asset_tracker_restapi(username=session["jira_username"], password=session["jira_password"])
    asset_id = request.form['object_id']
    if request.form['comment']:
        comment = request.form['comment']
    else:
        comment = "Uploaded by %s" % session["jira_username"]
    asset_api.upload_file_to_object(asset_id, request.files['asset_image'], comment)
    return redirect(url_for("asset.asset", asset_id=asset_id))


@bp.route("/asset_action/<string:asset_id>/<string:asset_action>/<int:action_id>")
def asset_action(asset_id, asset_action, action_id):
    # Take some action from the main menu, calls an asset tracker api that is just a dict
    asset_api = asset_tracker_restapi(username=session["jira_username"], password=session["jira_password"])
    if action_id != 0:
        asset_action = asset_api.action_id_to_action(action_id)
    object_type_id = asset_api.get_asset_object_type_by_id(asset_id)
    asset_dict = {'object_id': asset_id, 'object_type_id': object_type_id, 'Action Field': asset_action}
    asset_id = asset_api.update_asset_from_dict(asset_dict)
    return redirect(url_for("asset.asset", asset_id=asset_id))
