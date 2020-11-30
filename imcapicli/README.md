# IMC Scripts

## Available Scripts/Utilities

*Ensure steps described in [Installation](#installation) section are complete.*

- [logparse](#logparse)

## Installation

- clone this repo:  `git clone https://github.com/Pack3tL0ss/imc-scripts.git`
- Configure VirtualEnv

    ```bash
    cd imc-scripts
    python3 -m virtualenv venv # may require full path to python3.exe on Windows if python3.exe is not in PATH
    ```

    > if you get an error similar to 'No module ... virtualenv' you probably need to either `apt install python3-virtualenv` (Linux) or `python3 -m pip install virtualenv` (Linux and Windows (Assuming python3.exe is in path))

    ```bash
    # Linux
    venv/bin/python -m pip install --upgrade pip  # not required but good practice to ensure the pip in the venv is up to date
    venv/bin/python -m pip install -r requirements.txt

    # Windows
    \venv\Scripts\python -m pip install --upgrade pip  # not required but good practice to ensure the pip in the venv is up to date
    \venv\Scripts\python -m pip install -r requirements.txt
    ```

- Create Configuration File

    ```bash
    cp config.yaml.example config.yaml
    nano config.yaml  # or vim, vi... editor of your choice.
    # edit values based on environment then save and exit
    ```

    ***config.yaml Should look like:***

    ```yaml
    imc:                                    # required imc main key, all settings for imc are indented below (2 spaces per yaml spec)
      user: wade                            # username with ability to access imc API
      pass: 'yourpasshere'                  # password
      address: 'imc.consolepi.org'          # fqdn or ip address of IMC server
      port: '443'                           # port used to access IMC via http/https
      ssl: true                             # use https if true, http if false (cert validation is disabled for https)
      logparse:                             # required for logparse script
        user: imc-svc-user                  # The username imc utilizes to gain CLI access to managed devices
        file: in/imcupgdm.2020-11-17.txt    # The logfile to parse (best to place in the in subdirectory as it's ignored by git)
    ```


## logparse

- Will parse log file defined in config for various errors and return results

### USAGE

*Ensure steps described in [Installation](#installation) section are complete.*

#### Linux
```bash
# From the imc-scripts directory
source venv/bin/activate

# show help text with available commands
./logparser.py --help
Usage: logparser.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help                          Show this message and exit.

Commands:
  get-all-lines
  get-v1-devs

--help

# show help text with options for get-all-lines (get-v1-devs has no options)
./logparser.py get-all-lines
Usage: logparser.py get-all-lines [OPTIONS]

Options:
  --include TEXT
  --exclude TEXT
  --help          Show this message and exit.

# parse imc log file defined in config.yaml and extract devices that failed due to lack of SSHv2 support on the device
# gather ip address for each device from IMC API.  generates output file `ssh_v1_devices.cfg` in `out` directory.
./logparser.py get-v1-devs
6012: 10.0.30.56
6016: 10.0.99.45
6018: 10.0.99.46
4847: 10.0.24.33


Found 4 devices with errors indicating they require SSHv1 (parsed from log).

Formatted list of IPs sent to out/ssh_v1_devices.cfg
```

#### Windows
```powershell
# From the imc-scripts directory
venv\bin\Scripts\activate

# show help text with available commands
python logparser.py --help
Usage: logparser.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help                          Show this message and exit.

Commands:
  get-all-lines
  get-v1-devs

--help

# show help text with options for get-all-lines (get-v1-devs has no options)
python logparser.py get-all-lines
Usage: logparser.py get-all-lines [OPTIONS]

Options:
  --include TEXT
  --exclude TEXT
  --help          Show this message and exit.

# parse imc log file defined in config.yaml and extract devices that failed due to lack of SSHv2 support on the device
# gather ip address for each device from IMC API.  generates output file `ssh_v1_devices.cfg` in `out` directory.
python logparser.py get-v1-devs
6012: 10.0.30.56
6016: 10.0.99.45
6018: 10.0.99.46
4847: 10.0.24.33


Found 4 devices with errors indicating they require SSHv1 (parsed from log).

Formatted list of IPs sent to out/ssh_v1_devices.cfg
```

