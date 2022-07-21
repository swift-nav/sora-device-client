Sora Device Client
=================

<!-- vim-markdown-toc GFM -->

* [Installing](#installing)
  * [Dependencies](#dependencies)
    * [Buf](#buf)
    * [Python](#python)
* [Command-Line Client](#command-line-client)
  * [Configuration](#configuration)
    * [Configuration file](#configuration-file)
    * [Environment variables](#environment-variables)
    * [Command-line argument](#command-line-argument)
* [Running the daemon](#running-the-daemon)

<!-- vim-markdown-toc -->

The Sora Device Client provides a set of simple tools to connect your device to Sora.

The Sora Device Client consists of:

 - A command-line client - the simplest way to connect to Sora
 - A Python client library - for deeper integration and customization

# Installing
## Dependencies

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
make grpc
```

### Python
You need to install python 3.10.
```bash
brew install python@3.10
```
Although we recommend using something line [pyenv](https://github.com/pyenv/pyenv)
or [asdf](https://asdf-vm.com/) to manage your python versions.

We manage python dependencies with [Poetry](https://python-poetry.org/).

They are recorded in `pyproject.toml`. Note that there are dev and prod dependencies.

You will need to install the poetry cli to use it
```bash
brew install poetry
```
And then install the dependencies:
```bash
poetry install
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

 - Mac OS: `~/.config/sora-device-client` and `~/Library/Application Support/sora-device-client`
 - Other Unix: `~/.config/sora-device-client` and `/etc/sora-device-client`
 - Windows: `%APPDATA%\sora-device-client` where the `APPDATA` environment variable falls back to `%HOME%\AppData\Roaming` if undefined

Default values are specified [here](sora-device-client/config_default.yaml).

### Environment variables

Any parameter from the configuration file can also be specified as an
environment variable. The environment variable name takes the format
`SORA_DEVICE_CLIENT_PARAMETER` where the parameter name is converted to upper-case. Where
nested parameters are used, they can be joined with a double underscore.

Examples:

```bash
export SORA_DEVICE_CLIENT_PORT=1234
export SORA_DEVICE_CLIENT_SOURCES__TCP__HOST=192.168.0.123
```

Where the same parameter is set, environment variables take precedence over config files.

### Command-line argument

For documentation on the available command-line arguments, run
```bash
poetry run daemon --help
```

Command line arguments have the highest precedence and will override
configuration from environment variables or config files.

# Running the daemon

```bash
poetry run daemon [ARGS]
```
