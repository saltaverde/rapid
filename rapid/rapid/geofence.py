from rapid.settings import GEOFENCE_USERS_URL, GEOFENCE_RULES_URL
import requests
import xml.etree.ElementTree as ET

"""
Wrapper functions for the Geofence REST API
"""

def addGeofenceUser(username, password, email):

    xml_template = '<user enabled="true" admin="false">\
                      <name></name>\
                      <password></password>\
                      <emailAddress></emailAddress>\
                    </user>'

    xml_root = ET.fromstring(xml_template)

    xml_root.find('name').text = username
    xml_root.find('password').text = password
    xml_root.find('emailAddress').text = email

    payload_xml = ET.tostring(xml_root)

    headers = {'Content-Type':'text/xml'}
    response = requests.post(GEOFENCE_USERS_URL, data=payload_xml, headers=headers)

    return response

def addGeofenceRule(username=None, layer=None, grant='ALLOW'):

    xml_template = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\
                        <rule grant="ALLOW">\
                            <position value="1" position="offsetFromBottom"/>\
                            <username></username>\
                            <instance>\
                                <name>default-gs</name>\
                            </instance>\
                            <workspace>rapid</workspace>\
                            <layer></layer>\
                        </rule>'

    xml_root = ET.fromstring(xml_template)

    if username is not None:
        xml_root.find('username').text = username
    else:
        xml_root.remove(xml_root.find('username'))

    if layer is not None:
        xml_root.find('layer').text = layer
    else:
        xml_root.remove(xml_root.find('layer'))

    xml_root.attrib['grant'] = grant
    
    payload_xml = ET.tostring(xml_root)

    headers = {'Content-Type':'text/xml'}
    response = requests.post(GEOFENCE_RULES_URL, data=payload_xml, headers=headers)

    return response

def removeGeofenceRule(rule_id):

    if rule_id is not None:
        response = requests.delete(GEOFENCE_RULES_URL + '/id/' + str(rule_id))

        return response.status_code

    else:
        return None

def removeGeofenceUser(username):
    """
    Removes the user from Geofence and all rules associated only with him.
    """

    user_rules = getGeofenceRules(username)

    if user_rules is not None:
        for rule in user_rules.iter('rule'):
            status_code = removeGeofenceRule(rule.find('id').text)
            if status_code != 200:
                print "Unable to remove rule " + rule.find('id').text + ". Status code = " + status_code

    response = requests.delete(GEOFENCE_USERS_URL + '/name/' + username)

    return response


def getGeofenceRules(username=None):
    """
    Returns an ElementTree xml object of rules associated only with the user.
    """

    response = requests.get(GEOFENCE_RULES_URL + '?userName=' + username)

    return response