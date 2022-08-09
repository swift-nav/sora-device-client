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
    * [Command-line argument](#command-line-argument)

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

Here are the paths for each platform for the config file:

 - Mac OS: `~/Library/Application Support/sora-device-client/config.toml`.
 - Other Unix: `$XDG_CONFIG_HOME/sora-device-client/config.toml`. Usually this is `~/.config/sora-device-client/config.toml`.
 - Windows: `%APPDATA%\SwiftNav\sora-device-client` where the `APPDATA` environment variable falls back to `%HOME%\AppData\Roaming` if undefined

Copy the default config file to one of the following locations:
```bash
mkdir -p ~/.config/sora-device-client
cp sora-device-client/config_example.toml ~/.config/sora-device-client
```
You will most likely have to edit the `driver` section to work with the location source for your system.

### Command-line argument

For documentation on the available command-line arguments, run
```bash
poetry run sora --help
```
