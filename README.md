Sora Device Client
=================

<!-- vim-markdown-toc GFM -->

* [Installing](#installing)
  * [Dependencies](#dependencies)
    * [Package Manger](#package-manger)
    * [Buf](#buf)
    * [Python Interpreter](#python-interpreter)
    * [Python Dependencies](#python-dependencies)
* [Command-Line Client](#command-line-client)
  * [Configuration file](#configuration-file)
  * [Running](#running)
    * [Login](#login)
    * [Start](#start)
    * [Logout](#logout)
  * [Data file](#data-file)

<!-- vim-markdown-toc -->

The Sora Device Client provides a set of simple tools to connect your device to Sora.

The Sora Device Client consists of:

 - A command-line client - the simplest way to connect to Sora
 - A Python client library - for deeper integration and customization

# Installing

## Dependencies

You should only need to follow these steps once per machine you are setting up to run the sora-device-client on.

### Package Manger
You will most likely need a package manager to install the other dependencies. Use the one that is canonical for your distribution, for example: `apt`, `dnf`, `yum`, `pacman`.

For macOS, it is recommend to use [homebrew](https://brew.sh/). For windows, something like [chocolately](https://chocolatey.org/) will do.

### Python Interpreter
You need to install python 3.10. See <https://www.python.org/downloads/> for download instructions.
On macOS, you can use homebrew as well:
```bash
brew install python@3.10
```

## Option 1) Install with `pip` from PyPI.

~~NOT YET FINALIZED~~

## Option 2) Install with `pip` from Github artifact.

Wheels are built with Github Actions. You can get the latest run by going to

https://github.com/swift-nav/sora-device-client/actions/workflows/fmt.yaml?query=branch%3Amain

, clicking the **first item** there, going to **Artifacts**, and downloading **sora.whl**.

If you unzip `sora.whl.zip`, you'll see a single `.whl` file. Install it with `pip`:

```sh
unzip sora.whl.zip
pip install sora_device_client-*-py3-none-any.whl
```

## Option 3) Install from this checked-out repo.

This requires the `buf` tool. Full installation instructions and options are
[here](https://docs.buf.build/installation), or simply on Mac/Linux with Brew with
```bash
brew install bufbuild/buf/buf
```

Once `buf` is installed,

```sh
# check out this repo,
git clone github.com/sora/sora-device-client
cd sora-device-client

# generate code,
make sora

# install,
pip install .

# and check it works.
sora --version
```


# Command-Line Client

## Configuration file
Copy the default config file to the appropriate location. `sora` will tell you where it should go:

```sh
sora paths
# Example output:
# Configuration folder: (your config.toml needs to go in here)
#     /home/jwhitaker/.config/sora-device-client
#
# Data folder: (other runtime data gets stored in here)
#     /home/jwhitaker/.local/share/sora-device-client
```

`sora` will also give you an example configuration:
```sh
sora example-config
# ==============================================================================
# Sora Device Client configuration
# ==============================================================================
#
# ...
# 
```

Putting them together, you can set up a config file in the right location, and edit it:

```sh
mkdir -p /home/jwhitaker/.config/sora-device-client/ # (configuration folder from `sora paths`)
sora example-config > /home/jwhitaker/.config/sora-device-client/config.toml 
notepad /home/jwhitaker/.config/sora-device-client/config.toml # or whatever
```

You will most likely have to edit the `[location.driver]` section to work with the location source for your system.

If you are connecting to a GNSS location source over the network, it will be something like:
```toml
[location.driver.tcp]
host = "localhost"
port = 55555
```
However if you are connecting over a serial or USB port:
```toml
[location.driver.serial]
port = "/dev/tty.usbmodem14401"
baud = 115200
```
The value of `port` will be highly hardware specific. Some values that are known to have worked are: `/dev/ttyACM0`, `/dev/ttyUSB0`, `/dev/tty.usbmodem14401`.
If you have Swift hardware and have installed the Swift Console: https://support.swiftnav.com/support/solutions/articles/44001903699-installing-swift-console, the value used to connect it to your swift device will work.

Also note that sometimes non privileged users do not have permission to read and write to the device. The easiest way to obtain these permissions is to add your user to the group of the device. For example if it is `/dev/ttyACM0`, the group to add yourself to may be obtained with:
```bash
stat -c "%G" /dev/ttyACM0
```
See [here](https://wiki.archlinux.org/title/users_and_groups#Other_examples_of_user_management) for how to add a user to a group on Linux. You may need to log out of and log in to the operating system session again. On macOS and Windows, the instructions are too varied to list here. Please research how to do this for your combination of OS and OS version.

## Running

```
Once installed, the `sora` command will be in the path:
```bash
sora --help
```

### Login
To authenticate with a sora server, run
```bash
sora login
```
and follow the interactive procedure. You will need access to a web browser.

### Start
After authentication, you can stream data to the sora server with
```bash
sora --verbose start
```

### Logout
If you wish to use a difference set of credentials on the same hardware, you can clear them with
```bash
sora logout
```

## Data file
There is also a data file called `data.toml` that is used to store data that is generated by `sora login`. Typically, running `sora logout` will clear this file.
If you need to manually remove it, its location is is the `Data path` location from the output of

```sh
sora paths
```
