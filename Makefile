include .api-version

.PHONY: build
build: sora .venv

.PHONY: shell
shell: build
	poetry shell

sora: buf.gen.yaml .api-version
	buf generate buf.build/swift-nav/sora-api:$(SORA_API_REF)

.venv: sora pyproject.toml poetry.toml poetry.lock
	poetry lock --check
	poetry install

.PHONY: clean
clean:
	git clean -ffidx -e Session.vim
