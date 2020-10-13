from jira_requests import jira_requests
import json
import pprint


class asset_tracker_restapi:
    def __init__(self, username=None, password=None):
        self.my_request = jira_requests(username=username, password=password)

    def add_asset(self, asset_dict):
        #  This is only for testing, it was used to generate a large number of items
        json_dict = {'objectTypeId': asset_dict['object_type_id'],
                     # 'categoryName': item_dict['category'],
                     'attributes': [
                                {'objectTypeAttributeId': 2, 'objectAttributeValues': [{'value': asset_dict['asset_name']}]},
                                # {'objectTypeAttributeId': item_dict[''], 'value': [item_dict['asset_name']]},
                                {'objectTypeAttributeId': 5, 'objectAttributeValues': [{'value': asset_dict['tracking_hist']}]},  # Tracking Hist
                                {'objectTypeAttributeId': 6, 'objectAttributeValues': [{'value': asset_dict['rad_info']}]},  # Tracking Hist
                            #    {'typeName': 'system.description', 'values': [item_dict['asset_desc']]},
                                {'objectTypeAttributeId': 7, 'objectAttributeValues': [{'value': True}]}
                            #    {'typeName': 'nexo.asset.shipping.origin', 'values': [item_dict['origin']]},
                            #    {'typeName': 'nexo.asset.image', 'values': [item_dict['asset_image']]}
                                ]
                    }
        #print(json_dict)
        inserted_asset = self.my_request.post_data("object/create", json_dict)
        print(inserted_asset.json())
        return inserted_asset

    def upload_file_to_object(self, asset_id, file_object, comment):
        # Upload a file to an asset/object with a comment
        operator = "attachments/object/" + str(asset_id)
        file_added = self.my_request.post_file_upload(operator, file_object, comment)
        return asset_id

    def get_file_from_object(self, asset_id, file_url):
        # Request a single file from an asset
        response = self.my_request.get_data_file_url(file_url)
        return response

    def get_asset_attachments(self, asset_id):
        # Get a list of all file attachments the asset has
        asset_attachments = self.my_request.get_data("attachments/object/%s" % str(asset_id))
        return asset_attachments.json()

    def build_json_assets_dict(self, asset_dict):
        # This builds up the json for creating or updating an object/asset from a dict of attributes.
        json_dict = {}
        attribute_list = []
        json_dict.update({'objectTypeId': asset_dict['object_type_id']})
        for asset_attribute in asset_dict:  # Iterate though all the attributes so we can bunch them together into a dict of value lists
            if asset_attribute != "object_id" and asset_attribute != "object_type_id":
                attribute_id = self.get_attribute_id_from_name(asset_dict['object_type_id'], asset_attribute)
                attribute_list.append({'objectTypeAttributeId': attribute_id, 'objectAttributeValues': [{'value': asset_dict[asset_attribute]}]})
                json_dict.update({'attributes': attribute_list})
        return json_dict

    def add_asset_from_dict(self, asset_dict):
        # Add an asset, this is processed via a form dictionary with the appropriate information for the object schema
        json_dict = self.build_json_assets_dict(asset_dict)
        #  Inserts are run through a POST request
        inserted_asset = self.my_request.post_data("object/create", json_dict).json()
        return inserted_asset['id']

    def update_asset_from_dict(self, asset_dict):
        # Update an asset via a dict that is passed in from a form
        json_dict = self.build_json_assets_dict(asset_dict)
        #  Updates are required to go through a PUT request
        updated_asset = self.my_request.put_data("object/%s" % str(asset_dict['object_id']), json_dict).json()
        return updated_asset['id']

    def get_attribute_id_from_name(self, object_type_id, attribute_name):
        # If we pass an attribute name then we can get it's corresponding ID
        attribute_dict = self.get_object_type_attributes(object_type_id)
        for attribute in attribute_dict:
            if attribute['name'] == attribute_name:
                return attribute['id']
        print("Could not find attribute id for attribute name : %s" % attribute_name)
        return 0

    def get_object_types_for_schema(self, schema_id):
        # Get all available object types / catagories for assets that are under a specific scehma
        object_types = self.my_request.get_data("objectschema/%s/objecttypes/flat" % str(schema_id))
        return self.parse_object_types_list(object_types)

    def parse_object_types_list(self, response):
        object_types_list = []
        output = response.json()

        for my_object_type in output:
            if 'description' not in my_object_type:
                my_object_type.update({'description': ""})
            object_type_dict = {'id': my_object_type['id'],
                                'name': my_object_type['name'],
                                'description': my_object_type['description']}
            object_types_list.append(object_type_dict)
        return object_types_list

    def get_object_type_attributes(self, object_type_id):
        object_type_attributes = self.my_request.get_data("objecttype/%s/attributes" % str(object_type_id))
        # pprint.pprint(object_type_attributes.json())
        if object_type_attributes == 0:
            return 0
        return self.parse_object_type_attributes(object_type_attributes)

    def parse_object_type_attributes(self, response):
        object_type_attributes_list = []
        output = response.json()

        for my_object_attrib in output:
            object_type_attributes_dict = {'id': my_object_attrib['id'],
                                           'name': my_object_attrib['name'],
                                           'hidden': my_object_attrib['hidden'],
                                           'editable': my_object_attrib['editable'],
                                           'field_type': my_object_attrib['defaultType']['name'],
                                           'options': my_object_attrib['options'].split(',')}
            if 'description' in my_object_attrib:
                object_type_attributes_dict.update({'description': my_object_attrib['description']})
            object_type_attributes_list.append(object_type_attributes_dict)
        return object_type_attributes_list

    def search_assets(self, field, search_text):
        '''Search for asset using field and value for field as input'''
        asset_query = field + '=' + search_text
        params_dict = {'query': asset_query}
        assets = self.my_request.get_data("search", params_dict)
        return assets

    def get_asset_field_from_json_by_name(self, entry_name, asset_data, entry_value='value'):
        my_entry_value = ""
        for entry in asset_data:  # asset data is a list of dict's so we need to iterate over to find the Name entry
            if entry['name'] == entry_name:
                my_entry_value = entry[entry_value]
                break
        return my_entry_value

    def get_asset_object_type_by_id(self, asset_id):
        operator = "object" + "/" + str(asset_id)
        response = self.my_request.get_data(operator)
        if response == 0:
            return 0
        output = response.json()
        return output['objectType']['id']

    def get_asset_by_id(self, asset_id):
        operator = "object" + "/" + str(asset_id)
        asset = self.my_request.get_data(operator)
        if asset != 0:
            return self.parse_asset(asset)
        else:
            return 0

    def parse_asset(self, response):
        '''Take in a response request asset from (JIRA) and parse the data into a single easy to read list of dictionary'''
        output = response.json()
        asset_list = []
        for attribute in output['attributes']:
            asset_dict = {'id': attribute['objectTypeAttribute']['id'],
                          'name': attribute['objectTypeAttribute']['name'],
                          'editable': attribute['objectTypeAttribute']['editable'],
                          'field_type': attribute['objectTypeAttribute']['defaultType']['name'],
                          'value': attribute['objectAttributeValues'][0]['value']
                          }
            if 'description' in attribute['objectTypeAttribute']:
                asset_dict.update({'description': attribute['objectTypeAttribute']['description']})
            asset_list.append(asset_dict)

        return asset_list

    def get_object_attribute_history(self, asset_id, object_attribute):
        asset_history_list = []
        operator = "object" + "/" + str(asset_id) + "/history"
        full_asset_hist = self.my_request.get_data(operator).json()
        for my_asset_hist in full_asset_hist:
            asset_history_dict = {}
            if 'affectedAttribute' in my_asset_hist:
                if my_asset_hist['affectedAttribute'] == object_attribute:
                    asset_history_dict.update({'person_fullname': my_asset_hist['actor']['displayName']})
                    asset_history_dict.update({'person_username': my_asset_hist['actor']['name']})
                    asset_history_dict.update({'change_date': my_asset_hist['created']})
                    asset_history_dict.update({'old_value': my_asset_hist['oldValue']})
                    asset_history_dict.update({'new_value': my_asset_hist['newValue']})
                    asset_history_list.append(asset_history_dict)
        return asset_history_list

    def get_asset_connected_tickets(self, asset_id):
        operator = "objectconnectedtickets" + "/" + str(asset_id) + "/tickets"
        asset_tickets = self.my_request.get_data(operator).json()
        return asset_tickets['tickets']

    def action_id_to_action(self, action_id):
        action = ""
        if action_id == 1:
            action = "Recieved"
        elif action_id == 2:
            action = "Shipped"
        elif action_id == 3:
            action = "Cleaned"
        elif action_id == 4:
            action = "Out for a beer"
        return action

    def test(self):
        print("Hello!, username is : %s, password is : %s" % (self.my_request.username, self.my_request.password))
