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


### Buf

The Sora API uses a gRPC interface and the API libraries are built by
[buf.build](https://buf.build/).

This requires the `buf` tool. Full installation instructions and options are
[here](https://docs.buf.build/installation), or simply
```bash
brew install bufbuild/buf/buf
```

Then the api libraries can be generated with:
```bash
make
```

### Python Interpreter
You need to install python 3.10. See <https://www.python.org/downloads/> for download instructions.
On macOS, you can use homebrew as well:
```bash
brew install python@3.10
```
Although we recommend using something like [pyenv](https://github.com/pyenv/pyenv)
or [asdf](https://asdf-vm.com/) to manage your python versions.

### Python Dependencies

We manage python dependencies with [Poetry](https://python-poetry.org/).
They are recorded in `pyproject.toml`. Note that there are dev and prod dependencies.
You will need to install the poetry cli to use it. On macOS this may be done with homebrew.
```bash
brew install poetry
```
For platform independent installation instruction, see <https://python-poetry.org/docs/#installing-with-pipx>. Note that asdf can also manage poetry installations: <https://github.com/asdf-community/asdf-poetry>.

And then install the dependencies:
```bash
poetry install
```

# Command-Line Client

## Configuration file
Copy the default config file to one of the locations in the table below.
| OS                    | Path                                                                                               |
|-----------------------|----------------------------------------------------------------------------------------------------|
| MacOS:                | `~/Library/Application Support/sora-device-client`                                                         |
| Other Unix:           | `~/.config/sora-device-client` or `$XDG_CONFIG_HOME/sora-device-client`, if defined                |
| Win XP (not roaming): | `C:\Documents and Settings\<username>\Application Data\SwiftNav\sora-device-client`                |
| Win XP (roaming):     | `C:\Documents and Settings\<username>\Local Settings\Application Data\SwiftNav\sora-device-client` |
| Win 7  (not roaming): | `C:\Users\<username>\AppData\Local\SwiftNav\sora-device-client`                                    |
| Win 7  (roaming):     | `C:\Users\<username>\AppData\Roaming\SwiftNav\sora-device-client`                                  |

For example, if you are on macOS:
```bash
mkdir -p "~/Library/Application Support/sora-device-client"
```

```bash
cp sora_device_client/config_example.toml ~/Library/Application\ Support/sora-device-client/config.toml
```
Source: https://github.com/ActiveState/appdirs/blob/7af32e0b1fe57070ae8b5a717cdaebc094449518/appdirs.py#L187-L190

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
The value of `port` will be highly hardware specific some values that are known to have worked are: `/dev/ttyACM0`, `/dev/ttyUSB0`, `/dev/tty.usbmodem14401`.
If you have Swift hardware and have installed the Swift Console: https://support.swiftnav.com/support/solutions/articles/44001903699-installing-swift-console, the value used to connect it to your swift device will work.

Also note that sometimes non privileged users do not have permission to read and write to the device. The easiest way to obtain these permissions is to add your user to the group of the device. For example if it is `/dev/ttyACM0`, the group to add yourself to may be obtained with:
```bash
stat -c "%G" /dev/ttyACM0
```
See [here](https://wiki.archlinux.org/title/users_and_groups#Other_examples_of_user_management) for how to add a user to a group. You may need to log out of and log in to the operating system session again.

## Running
To run the command-line client, launch a shell from poetry:
```bash
poetry shell
```
In the new shell, the `sora` command will be in the path:
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
If you need to manually remove it, its location typically is:

| OS                    | Path                                                                                               |
|-----------------------|----------------------------------------------------------------------------------------------------|
| MacOS:                | `~/Library/Application Support/sora-device-client`                                                 |
| Other Unix:           | `~/.local/share/sora-device-client` or `$XDG_DATA_HOME/sora-device-client`, if defined             |
| Win XP (not roaming): | `C:\Documents and Settings\<username>\Application Data\SwiftNav\sora-device-client`                |
| Win XP (roaming):     | `C:\Documents and Settings\<username>\Local Settings\Application Data\SwiftNav\sora-device-client` |
| Win 7  (not roaming): | `C:\Users\<username>\AppData\Local\SwiftNav\sora-device-client`                                    |
| Win 7  (roaming):     | `C:\Users\<username>\AppData\Roaming\SwiftNav\sora-device-client`                                  |

Source: https://github.com/ActiveState/appdirs/blob/7af32e0b1fe57070ae8b5a717cdaebc094449518/appdirs.py#L66-L72
