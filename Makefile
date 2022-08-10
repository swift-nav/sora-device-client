SORA_API_REF=3674176de04d453b9d89dab9e316232a
SOURCES := $(shell find sora_device_client -name "*.py")

# If the first argument is "run"...
ifeq (run,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "run"
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
	# $(eval $(RUN_ARGS):dummy;@:)
endif

.PHONY: build
build: sora .venv

.PHONY: run
run: build
	@poetry run sora $(RUN_ARGS)

sora: buf.gen.yaml
	buf generate buf.build/swift-nav/sora-api:$(SORA_API_REF)

.venv: sora $(SOURCES) pyproject.toml poetry.toml poetry.lock
	poetry install

.PHONY: clean
clean:
	git clean -ffidx -e Session.vim
