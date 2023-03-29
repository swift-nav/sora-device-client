# Installing development versions

### Option 1) Install from this checked-out repo.

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

### Option 2) Install with `pip` from Github artifact.

Wheels are built with Github Actions. You can get the latest run by going to

https://github.com/swift-nav/sora-device-client/actions/workflows/fmt.yaml?query=branch%3Amain

, clicking the **first item** there, going to **Artifacts**, and downloading **sora.whl**.

If you unzip `sora.whl.zip`, you'll see a single `.whl` file. Install it with `pip`:

```sh
unzip sora.whl.zip
pip install sora_device_client-*-py3-none-any.whl
```


## Buf

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

## Python Dependencies

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

# Running
To run the command-line client, launch a shell from poetry:
```bash
poetry shell
```
In the new shell, the `sora` command will be in the path:
```bash
sora --help
```
