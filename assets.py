from jira_requests import jira_requests
from asset_tracker_restapi import asset_tracker_restapi
import pprint
import json
import random
import string
import sys

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    #print("Random string of length", length, "is:", result_str)
    return result_str


asset_api = asset_tracker_restapi()
#myjira = jira_requests()

#if myjira.verify_auth() != 0:
#    print("Auth Failed!!")
#    exit()
#item_dict['object_type_id']
#asset_api.test()
#myjson = myitem.list_catagories()
#print(myjson.json())
#items = myitem.get_all_items_in_catagory("Electrical")
#print(items.json())
#myitems = myitem.parse_multiple_items_into_list(items)
#pprint.pprint(items.json())
my_dict = {'rad_info': 6}
#-----
#for item in range(2000, 500000):
#    mydict = {'object_type_id': 1, 'part_name': get_random_string(10), 'tracking_hist': get_random_string(500), 'rad_info': get_random_string(1000)}
#    myitem.add_item(item_dict=mydict)
#    print("Progress : ", item)
#print(myjira.get_data("item", "").text)
#myitem.
#items = myitem.search_items("id", "10312")
#print(items.json())
#print(items.text)
#items = myitem.get_item_by_id("46")
#pprint.pprint(myitem.get_object_types_for_schema(1))
#pprint.pprint(asset_api.get_object_types_for_schema(schema_id=1))
#pprint.pprint(asset_api.get_object_type_attributes(2))
mydict = {'object_id': 66, 'object_type_id': 2, 'max_volatge': 12000}
issues = asset_api.get_asset_connected_tickets("46")
pprint.pprint(issues)
for issue in issues:
    print("-----")
    pprint.pprint(issue)
#pprint.pprint(asset_api.update_asset_from_dict(mydict))
#pprint.pprint(asset_api.get_object_attribute_history(66, "max_volatge"))
#pprint.pprint(asset_api.get_attribute_id_from_name(1, "received1"))
#print(myitem.parse_items(items))
#print(items.json())
#pprint.pprint(items.json())
#mine = items.json()
#for something in mine:
#    print(something)

#pprint.pprint(mine['attributes'])
#for i in mine['attributes']:
##    pprint.pprint(i['objectTypeAttribute'])
#    pprint.pprint(i['objectTypeAttribute']['id'])
#    print(i['objectTypeAttribute']['editable'])
#    pprint.pprint(i['objectTypeAttribute']['name'])
#    pprint.pprint(i['objectTypeAttribute']['defaultType']['name'])
#    if 'description' in i['objectTypeAttribute']:
#        pprint.pprint(i['objectTypeAttribute']['description'])
#
#    pprint.pprint(i['objectAttributeValues'][0]['value'])

#    print("-----")
