#!/usr/bin/env python3
# Copyright (c) 2020 wade
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


from imcapicli import config, imc
from pathlib import Path
from typing import Union
import typer
import json

app = typer.Typer()


DEVICES = {}
DEV_ID_MATCH = ["dev_id:", " ID: ", "DevID=", ",devID=", "Device Id:", "dev id: "]
DEV_IP_MATCH = ["ip: ", "DevIP =", "dev_ip ="]
ERR_STR = typer.style("ERROR:", fg=typer.colors.RED)
WAR_STR = typer.style("WARNING:", fg=typer.colors.YELLOW)

def get_lines(file: Path = None):
    if file is None:
        parse_file = config.config.get("imc", {}).get("logparse", {}).get("file")
        if not parse_file:
            typer.echo("no logparse file defined in config")
            raise typer.Exit(code=1)
        else:
            f = Path(parse_file)
    else:
        f = Path(file)

    if f.exists():
        with f.open() as _f:
            lines = _f.readlines()
        return lines
    else:
        typer.echo(f"{f} File Not Found")
        raise typer.Exit(code=1)


class ImcDev:
    def __init__(self, dev_id: int = None, dev_ip: str = None, steps: list = [], start: str = None,
                 pid: Union[int, list] = [], children: list = [], adapter: str = None, login_type: str = None):
        print("__init__")
        self._user = None
        self._userip = None
        self.dev_id = dev_id
        self.dev_ip = dev_ip
        self.steps = steps
        self.start = start
        if pid and isinstance(pid, (str, int)):
            pid = [int(pid)]
        elif pid is None:
            pid = []
        self.pid = pid
        self.children = children
        self.version = []
        self.adapter = adapter
        self.login_type = login_type
        if login_type:
            self.login_type = "ssh" if login_type == "2" else "!!NOT SSH!!"



    # def __call__(self, *args, **kwargs):
    #     self.update(*args, **kwargs)

    def __call__(self, dev_id: int = None, dev_ip: str = None, steps: list = [], start: str = None,
                 pid: int = [], children: list = [],  adapter: str = None, login_type: str = None,
                 **kwargs):
        print("__call__")
        self.dev_id = dev_id
        self.dev_ip = dev_ip
        self.steps = steps
        self.start = start
        if pid and isinstance(pid, (str, int)):
            pid = [int(pid)]

        _pid = [p for p in [*self.pid, *pid] if p not in self.pid]
        self.pid = _pid
        self.children = children
        self.version = []
        self.adapter = adapter
        if login_type:
            self.login_type = "ssh" if login_type == "2" else "!!NOT SSH!!"

        return self


    # def update(self, dev_id: int = None, dev_ip: str = None, steps: list = [], start: str = None,
    #            pid: int = [], children: list = [],  adapter: str = None, login_type: str = None,
    #            **kwargs):
    #     self.dev_id = dev_id
    #     self.dev_ip = dev_ip
    #     self.steps = steps
    #     self.start = start
    #     if pid and isinstance(pid, (str, int)):
    #         pid = [int(pid)]

    #     self.pid = [p for p in [*self.pid, *pid] if p not in self.pid]
    #     self.children = children
    #     self.version = []
    #     self.adapter = adapter
    #     self.login_type = "ssh" if login_type and login_type == "2" else "!!NOT SSH!!"



    @property
    def user(self):
        if hasattr(self, "_user"):
            return self._user

    @user.setter
    def user(self, new_value):
        self._user = self._hex_to_str(new_value)
        return self._user

    def _hex_to_str(var: Union[str, hex]):
        if var:
            return var if not isinstance(var, hex) else bytes.fromhex(var).decode("UTF-8")

    def __str__(self):
        return "\n".join(f"\t{k}: {v}" for k, v in self.__dict__)

    def __iter__(self):
        for k, v in self.__dict__:
            yield f"\t{k}: {v}"

# cli script output
def get_cli_output():
    lines = get_lines()
    _print = False
    for line in lines:
        if _print and line.strip() != "":
            if "[THREAD" in line:
                _print = False
                print("\n -------------- \n")
            else:
                print(line, end="")
        elif "Finished, result:" in line:
            _print = True

# @app.command()
def get_device_errors(error: str = typer.Argument(None)):
    cfg = config.config.get('imc', {}).get('logparse', {})
    parse_user = cfg.get('user')
    if not parse_user:
        typer.echo("imc, logparse, user is missing in config, this is the user IMC uses to log into devices")
        raise typer.Exit(code=1)

    lines = get_lines()
    _print = False
    dev_ip = ''
    dev_lines = []
    dev_ips = []
    _error = None
    for idx, line in enumerate(lines):
        if f"{parse_user}@" in line:
            dev_ip = line.split("@")[1].split("'")[0]
        if _print and line.strip() != "":
            if "[THREAD" in line:
                _print = False
                dev_lines.insert(0, f"\n -------{dev_ip}------- \n")
                if _error:
                    typer.echo("".join(dev_lines))
                    dev_ips.append(dev_ip)
                    _error = None
                dev_lines = []
            else:
                if "Not authorized to run this command" in line:
                    _error = "cmd_authz"
                dev_lines.append(
                    f'{idx}.  {line.replace("Not authorized to run this command", typer.style("Not authorized to run this command", fg=typer.colors.RED))}'
                    )
        elif "Finished, result:" in line:
            _print = True
            dev_ip = ''

    typer.secho("Devices with Comand Authorization Failures:", fg=typer.colors.MAGENTA)
    typer.echo("\n".join(dev_ips))

def get_threads() -> list:
    cur_thread = 0
    threads = []
    children = []
    lines = get_lines()
    for line in lines:
        if "THREAD(" in line:
            _thread = line.split("THREAD(")[-1].split(")")[0]
            if cur_thread != _thread:
                threads += [{_thread: children}]
                cur_thread = _thread
                children = []
            elif "spawn" in line and "pid:" in line:
                # print("child", line.split("pid:")[1].split(" ")[0].strip())
                threads[threads.index(cur_thread)].append(line.split("pid:")[1].split(" ")[0].strip())
    return threads

def _id_in_line(dev_id: Union[str, int], line: str) -> bool:
    return [True for _ in DEV_ID_MATCH if _ in line and str(dev_id) in line]


def get_attrs_from_line(line: str, dev: ImcDev = None) -> int:
    # class Line:
    #     def __init__(self, dev_id: str = None, dev_ip: str = None):
    #         self.dev_id = dev_id
    #         self.dev_ip = dev_ip

    #     def __bool__(self):
    #         return self.dev_id is not None

    _id, _ip, _adapter, _login_type, _start = None, None, None, None, None
    _thread = line.split("THREAD(")[-1].split(")")[0]
    for _ in DEV_ID_MATCH:
        if _ in line:
            _id = int(line.split(_)[-1].lstrip().split(" ")[0].split(",")[0].strip())
            for _ in DEV_IP_MATCH:
                if _ in line:
                    _ip = line.split(_)[-1].lstrip().split(" ")[0].split(",")[0].strip().rstrip(".")

            if "AdaptName=" in line:
                _adapter = line.split("AdaptName=")[-1].strip()
            if "Device login type is " in line:
                _login_type = line.split("Device login type is ")[-1].split(",")[0].strip()

    kwargs = {
        "dev_id": _id,
        "dev_ip": _ip,
        "start": _start,
        "pid": _thread,
        "adapter": _adapter,
        "login_type": _login_type
    }

    if dev is None:
        if _id is not None and DEVICES.get(_id):
            dev = DEVICES[_id](**kwargs)
        else:
            dev = ImcDev(**kwargs)

    if dev.dev_id:
        return dev


def get_id_from_line(line: str) -> int:
    for _ in DEV_ID_MATCH:
        if _ in line:
            return int(line.split("dev id:")[-1].lstrip().split(" ")[0].split(",")[0].strip())

def get_error_by_dev(dev_ip: str = None, dev_id: str = None) -> list:
    cur_thread = "999999"
    _dev_id = None
    _thread = 0
    threads = []
    children = []
    dev_results = None
    lines = get_lines()
    for idx, line in enumerate(lines):
        if "THREAD(" in line:
            _thread = line.split("THREAD(")[-1].split(")")[0]
            this_dev = get_attrs_from_line(line)
            if this_dev:
                _dev_id = this_dev.dev_id
                if this_dev.pid:
                    cur_thread = this_dev.pid[-1]
                DEVICES[_dev_id] = this_dev
            #     if _dev_id not in DEVICES:
            #         cur_thread = _thread
            #         DEVICES[_dev_id] = this_dev
            #         # ImcDev(dev_id=this_dev.dev_id, pid=_thread, dev_ip=this_dev.dev_ip)
            #     # elif this_dev.dev_ip and not DEVICES[_dev_id].dev_ip:
            #     #     DEVICES[_dev_id].dev_ip = this_dev.dev_ip
            # elif "CExecuter::CExecuter()" in line and "ID:" in line:
            #     _dev_id = line.split("ID:")[-1].strip()
            #     _start = line.split("[")[0].strip()
            #     if _dev_id not in DEVICES:
            #         cur_thread = _thread
            #         DEVICES[_dev_id] = ImcDev(dev_id=_dev_id, pid=_thread, start=_start)
                # DEVICES[_dev_id](dev_id=_dev_id, pid=_thread, start=_start)
            elif f"THREAD({cur_thread})" in line or (this_dev and _id_in_line(this_dev.dev_id, line)):
                if not _dev_id or _dev_id not in DEVICES:
                    print(f"Skipped line {idx} no key [{_dev_id}]:\n\t{line}")
                else:
                    if "Begin" in line:
                        DEVICES[_dev_id].steps += [" ".join(line.split("]")[2:]).strip()]
                    # elif "dev id: 6013, ip: 10.145.248.52"
                    if "spawn" in line and "pid:" in line:
                        DEVICES[_dev_id](pid=line.split("pid:")[1].split(" ")[0].strip())
                    elif "version = " in line:
                        DEVICES[_dev_id].version.append(line.split("version = ")[-1].strip())

        print(f"end parsing line {idx}")



    return DEVICES

def _init_DEVICES(lines: list) -> list:
    for line in lines:
        if "CExecuter::CExecuter()" in line and "ID:" in line:
            _thread = line.split("THREAD(")[-1].split(")")[0]
            _start = line.split("[")[0].strip()
            _id = line.split("ID:")[-1].strip()
            DEVICES[_id] = ImcDev(dev_id=_id, pid=_thread, start=_start)

    return DEVICES

@app.command()
def get_all_lines(include: str = None, exclude: str = None):
    lines = get_lines()
    if exclude and include:
        typer.echo_via_pager("".join([f'{idx}. {line}' for idx, line in enumerate(lines) if line.strip() != ""
                             and exclude not in line and include in line]))
    elif include:
        typer.echo_via_pager("".join([f'{idx}. {line}' for idx, line in enumerate(lines) if line.strip() != ""
                            and include in line]))
    elif exclude:
        typer.echo_via_pager("".join([f'{idx}. {line}' for idx, line in enumerate(lines) if line.strip() != ""
                             and exclude not in line]))
    else:
        if not include and not exclude:
            typer.echo_via_pager("".join([f'{idx}. {line}' for idx, line in enumerate(lines) if line.strip() != ""]))

@app.command()
def get_v1_devs() -> list:
    outfile = Path(__file__).parent.joinpath("out", "ssh_v1_devices.cfg")
    # typer.echo(f"outfile: {outfile.resolve()}")
    _capture = False
    id_map = {}
    v1_devs = []
    v1_cnt = 0
    lines = get_lines()
    for line in lines:
        if "dev id:" in line and "ip:" in line:
            _ip = line.split("ip: ")[-1].split(" ")[0].rstrip(".")
            id_map[int(line.split("dev id: ")[-1].split(",")[0])] = _ip

        if "THREAD" in line and "version 2 required by our configuration" in line:
            _capture = True
            _thread = line.split("THREAD(")[-1].split(")")[0]
            v1_cnt += 1
        elif _capture and "iDevID" in line:
            v1_devs.append(int.from_bytes(bytes.fromhex(line.strip().split("'")[1]), "big"))
            _capture = False

    imc_dev_dict = imc.device.get_all_devs(config.imc.creds, config.imc.url, by_id=True, verify=False)
    with outfile.open("w") as f:
        f.writelines("\n".join([imc_dev_dict.get(dev, {}).get('ip', f"Error: ip for device with id {dev} not found.") for dev in v1_devs]))
    typer.echo("\n".join([f"{dev}: {imc_dev_dict.get(dev, {}).get('label', '')}({imc_dev_dict.get(dev, {}).get('ip', 'Error ip Not Found')})"
                          for dev in v1_devs]))
    typer.echo(f"\nFound {v1_cnt} devices with errors indicating they require SSHv1 (parsed from log).")
    if outfile.exists():
        with outfile.open() as f:
            _errors = [True for line in f.readlines() if line.startswith("Error")]
            if _errors:
                typer.echo(f"\n{WAR_STR} SSHv1 device IPs exported to {outfile}, but {len(_errors)} errors were found (Unable to gather IP from from IMC) out of {v1_cnt} devices.\n")
            else:
                typer.echo(f"Formatted list of IPs sent to {outfile}\n")
    else:
        typer.echo(f"{ERR_STR} Unable to find {outfile.resolve()}\n")


# @app.command()
def get_cli_errors(include: str = typer.Argument(None), exclude: str = typer.Argument(None)) -> list:
    lines = get_lines()
    _capture = False
    id_map = {}
    v1_devs = []
    v1_cnt = 0
    input_params = ""
    for line in lines:
        if "dev id:" in line and "ip:" in line:
            _ip = line.split("ip: ")[-1].split(" ")[0].rstrip(".")
            id_map[int(line.split("dev id: ")[-1].split(",")[0])] = _ip

        if "THREAD" in line and "Failed to execute by cli method" in line:
            _capture = True
            _thread = line.split("THREAD(")[-1].split(")")[0]
            v1_cnt += 1
        elif _capture:
            if "InputParam " in line:
                input_params = line
            if _capture and "iDevID" in line:
                v1_devs.append(int.from_bytes(bytes.fromhex(line.strip().split("'")[1]), "big"))
                input_params = ""
                _capture = False

    print(v1_cnt)
    # cfg = config.config.get("imc")
    # imc_dev_list = imc.device.get_all_devs(config.imc.creds, config.imc.url, by_id=True, verify=False)
    typer.echo_via_pager(json.dumps({dev: (input_params, id_map.get(dev, "")) for dev in v1_devs}, indent=4))




if __name__ == "__main__":
    # lines = get_lines()
    app()
    # DEVICES = _init_DEVICES(lines)
    # v1_devs = get_v1_devs(lines)
    # v1_devs = get_cli_errors(lines)
    # for k, v in sorted(v1_devs.items()):
    #     print(v or k)
    # print(len(v1_devs))
    # get_cli_output()
    # get_error_by_dev()
