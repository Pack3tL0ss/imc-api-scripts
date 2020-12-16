#!/usr/bin/env python3
#
# Author: Wade Wells github/Pack3tL0ss

from pathlib import Path
from typing import Any
from pyhpeimc.auth import IMCAuth
import yaml
import os

REQUIRED_CONFIG = ["user", "pass", "address"]


class Config:
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.yaml_config = self.base_dir.joinpath('config.yaml')
        self.config = self.get_yaml_file(self.yaml_config) or {}
        self.debug = self.config.get("debug", os.getenv("DEBUG", False))
        self.imc = self.get_imc_auth()

    def __bool__(self):
        return len(self.config) > 0

    def __len__(self):
        return len(self.config)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    @staticmethod
    def get_yaml_file(yaml_config: Path):
        '''Return dict from yaml file.'''
        if yaml_config.exists() and yaml_config.stat().st_size > 0:
            with yaml_config.open() as f:
                try:
                    return yaml.load(f, Loader=yaml.SafeLoader)
                except ValueError as e:
                    print(f'Unable to load configuration from {yaml_config}\n\t{e}')

    def get_imc_auth(self) -> IMCAuth:
        '''Return IMCAuth object using Configuration from config file

        Returns:
            IMCAuth: pyhpeimc.auth.IMCAuth object
                Completed digest authentication attributes.
        '''
        if not self.config:
            print(f"!!! Config file: {self.yaml_config} not found or invalid.")
            return
        config = self.config.get("imc")
        if not config:
            print(f"!!! imc section missing from {self.yaml_config}")
            return
        _missing = [k for k in REQUIRED_CONFIG if k not in config]
        if _missing:
            print(f"!!! Required Configuration item {_missing} is missing from {self.yaml_config}")
            return
        elif not config.get("port") and not config.get("ssl") and not config["address"].startswith("http"):
            print(f"!!! 'port' and 'ssl' config values missing from {self.yaml_config} this is only allowed if the configured 'address'\n"
                  "includes the protocol i.e. (https://imc.consolepi.org)")
            return
        else:
            port = config.get("port")
            if config["address"].startswith("http"):
                proto_str = config.get("address").split(":")[0]
                if proto_str not in ["http", "https"]:
                    proto_str = None
                if not port and config["address"].count(":") != 2 and proto_str:
                    port = 9443 if proto_str == "https" else 8080
            else:
                proto_str = "https" if config.get("ssl") else "http"

            if not proto_str:
                print("Unable to determine protocol to use with IMC (http/https) based on configuration")
                return
            else:
            # def __init__(self, h_url, server, port, username, password):
                proto_str = f"{proto_str}://"
                address = config["address"].replace(f"{proto_str}://", "")
                return IMCAuth(proto_str, address, port, config["user"], config["pass"])

