


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
make .venv # this does `poetry install` and generates grpc stubs if necessary
```

## Running
To run the command-line client, launch a shell from poetry:
```bash
poetry shell
```
In the new shell, the `sora` command will be in the path:
```bash
sora --help
```
