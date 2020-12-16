#!/usr/bin/env python3
# coding=utf-8
# author: Pack3tL0ss ~ Wade Wells
# -*- coding: utf-8 -*-
"""
This module adds some new and override methods to the pyhpeimc module
"""
from imcapicli import MyLogger, Response, log
from typing import List, Union
# from . import Response

import requests
import os
import logging

from pyhpeimc.auth import HEADERS


DEV_SYSTEM = os.getenv("NAME") == "wellswa6"

# Note filter by dev_ids dev_ips not implemented yet
def get_config_center_dict(auth, url, dev_ids: Union[List[str], str] = None,
                           dev_ips: Union[List[str], str] = None, log: Union[MyLogger, logging.Logger] = log) -> Response:
    """Get Configuration Center details for all devices in IMC.

    Optionally filter return to include specified list of dev_ids, or dev ips

    Args:
        auth (IMCAuth Object): auth object from pyhpeimc module
        url (str): base url of imc
        dev_ids (List[str], optional): List of dev_ids to return. Defaults to None.
        dev_ips (List[str], optional): List of dev_ips to return. Defaults to None.

    Returns:
        dict: CfgCenter data for each device (name, model, SW Version, last Backup, latest avail SW)
              Returns data for all devices in system unless dev_id or dev_ip list is provided
    """
    f_url = url + "/imcrs/icc/deviceCfg/configurationCenter"
    log.info("Collecting info from Config Center for all devices")
    resp = Response(requests.get, f_url, auth=auth, headers=HEADERS, verify=False)
    if resp.ok:
        resp.output = {int(x["deviceId"]): {k: v for k, v in x.items() if k != "deviceId"} for x in  resp.output.get("deviceInfo", [])}
        log.debug(f"Collected Config Center Details for {len(resp.output)} devices")

    return resp


