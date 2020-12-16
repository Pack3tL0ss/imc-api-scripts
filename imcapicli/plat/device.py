#!/usr/bin/env python3
# coding=utf-8
# author: Pack3tL0ss ~ Wade Wells
# -*- coding: utf-8 -*-
"""
This module adds some new and override methods to the pyhpeimc module
"""

from typing import Union

import requests
import os

from pyhpeimc.auth import HEADERS

DEV_SYSTEM = os.getenv("NAME") == "wellswa6"

def get_all_devs(auth, url, network_address=None, category=None, label=None, start: int = 0,
                 size: int = None, order_by: str = "id", total: bool = False, by_id: bool = False,
                 by_ip: bool = False, **kwargs) -> Union[list, dict]:
    '''Get details for all devices managed by HPE IMC via API.

    Args:
        auth (IMCAuth): IMCAuth object
        url (str): Base url for IMC i.e. 'https://imc.consolepi.org:443'
        network_address (str, optional): Return details for a specific device by ip. Defaults to None.
        category (str, optional): Return details for all devices of a specific device category. Defaults to None.
        label (str, optional): Return details for a specific device by device label. Defaults to None.
        start (int, optional): The start record. Defaults to 0.
        size (int, optional): The number of items to return. Defaults to None.
        order_by (str, optional): What field the output is sorted by. Defaults to "id".
        total (bool, optional): Return the total number of devices or not. Defaults to False.
        by_id (bool, optional): If True will return a dict of dicts using dev id as key for each device. Defaults to False.
        by_ip (bool, optional): If True will return a dict of dicts using dev ip as key for each device. Defaults to False.

    Returns:
        dict: By default returns list of dicts with no key where attributes for each device are in the containing dict.
            Use by_id or by_ip to get a dict keyed by device id or ip.
    '''
    base_url = "/imcrs/plat/res/device?resPrivilegeFilter=false"
    if DEV_SYSTEM:
        print("Running With DEV_SYSTEM = True")
        end_url = f"&start={start}&size={size or 10}&orderBy={order_by}&desc=false&total={str(total).lower()}"
    else:
        end_url = f"&start={start}&size={size or 1000}&orderBy={order_by}&desc=false&total={str(total).lower()}"

    network_address = '' if not network_address else f"&ip={str(network_address)}"
    label = '' if not label else f"&label={str(label)}"
    category = '' if not category else f"&category{category}"

    f_url = url + base_url + str(network_address) + str(label) + str(category) + end_url

    dev_details, _link = None, None
    cnt = 1
    try:
        print(f"Sending Request {cnt} to IMC...", end=""); cnt += 1
        response = requests.get(f_url, auth=auth, headers=HEADERS, **kwargs)
        if response.status_code == 200:
            dev_details = response.json().get("device", {})
            _link = response.json().get("link")
            print(f"OK (details collected for {len(dev_details)} devices)")

        # if not called with return limits collect all devices via multiple calls if necessary
        if not size:
            while _link:
                if isinstance(_link, dict):
                    if _link["@rel"] == "next":
                        f_url = _link["@href"]
                    else:
                        break  # last record
                elif isinstance(_link, list) and _link[-1]["@rel"] == "next":
                    f_url = _link[-1]["@href"]
                else:
                    print("link key in response is not as expected")
                    break
                print(f"Sending Request {cnt} to IMC...", end=""); cnt += 1
                response = requests.get(f_url, auth=auth, headers=HEADERS, **kwargs)
                if response.status_code == 200:
                    _link = response.json().get("link")
                    dev_details = [*dev_details, *response.json().get("device", {})]
                    print(f"OK (details collected for {len(dev_details)} devices)")

    except Exception as e:
        # TODD Logging and exception
        print(f"Error\n{e}")

    # TODO return my Response object
    if dev_details:
        if by_id:
            return {int(i["id"]): i for i in dev_details}
        elif by_ip:
            return {i["ip"]: i for i in dev_details}
        else:
            return dev_details



    # try:
    #     if response.status_code == 200:
    #         dev_details = (json.loads(response.text))
    #         if len(dev_details) == 0:
    #             print("Device not found")
    #             return "Device not found"
    #         elif type(dev_details['device']) is dict:
    #             return [dev_details['device']]
    #         else:
    #             return dev_details['device']
    # except requests.exceptions.RequestException as error:
    #     return "Error:\n" + str(error) + " get_dev_details: An Error has occured"