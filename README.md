Kea Device Client
=================

The Kea Device Client provides a set of simple tools to connect your device to
Kea.

The Kea Device Client consists of:

 - A command-line client - the simplest way to connect to Kea
 - A Python client library - for deeper integration and customization

# Installing
## Dependencies
### Python
You need to install python 3.10.
```bash
brew install python@3.10
```
Although we recommend using something line [pyenv](https://github.com/pyenv/pyenv) or [asdf](https://asdf-vm.com/) to manage your python versions.

We manage python dependencies with [PDM](https://pdm.fming.dev/usage/dependency/)

They are recorded in `pyproject.toml`. Note that there are dev and prod
dependencies.

You will need to install the pdm cli to use it
```bash
brew install pdm
```

[Optional]You will need to choose a path to the python 3.10 installation created above.
```bash
pdm use
```

Download the dependencies with. This will prompt you to choose a python version if you did not complete the optional step above.
```bash
pdm sync
```

### Buf

The Kea API uses a gRPC interface and the API libraries are built by
[buf.build](https://buf.build/).

This requires the `buf` tool. Full installation instructions and options are
[here](https://docs.buf.build/installation), or simply
```bash
brew install bufbuild/buf/buf
```

#### Sign up
As well as installing the tool, you will need to:

1. Sign up to buf
2. Be added to the swift-nav organisation on buf.build as a member (ask #Narthana Epa on slack)
3. Login to the Buf Scheme Registry (BSR): https://docs.buf.build/tour/log-into-the-bsr

## Building the API libraries
```bash
make grpc
```

# Command-Line Client 

## Configuration

The command-line client can be configured via:
 - Configuration file
 - Environment variables
 - Command-line arguments

### Configuration file

Documentation is available in the [Example configuration file](examples/config.yaml).

The path to the configuration file can be passed as a command-line argument.

Here are the default search paths for each platform:

 - Mac OS: `~/.config/keaclient` and `~/Library/Application Support/keaclient`
 - Other Unix: `~/.config/keaclient` and `/etc/keaclient`
 - Windows: `%APPDATA%\keaclient` where the `APPDATA` environment variable falls back to `%HOME%\AppData\Roaming` if undefined

Default values are specified [here](keaclient/config_default.yaml).

### Environment variables

Any parameter from the configuration file can also be specified as an
environment variable. The environment variable name takes the format
`KEACLIENT_PARAMETER` where the parameter name is converted to upper-case. Where
nested parameters are used, they can be joined with a double underscore.

Examples:

```bash
export KEACLIENT_PORT=1234
export KEACLIENT_SOURCES__TCP__HOST=192.168.0.123
```

Where the same parameter is set, environment variables take precedence over
config files.

### Command-line argument

For documentation on the available command-line arguments, run
```bash
pdm -v run python -m keaclient.daemon --help
```

Command line arguments have the highest precedence and will override
configuration from environment variables or config files.

## Running the daemon

```bash
pdm -v run python -m keaclient.daemon [ARGS]
```
