include .api-version

.PHONY: build
build: sora .venv

.PHONY: shell
shell: build
	poetry shell

sora: buf.gen.yaml .api-version .venv/bin/protoc-gen-mypy
	poetry run buf generate buf.build/swift-nav/sora-api:$(SORA_API_REF)
	touch sora

.venv/bin/protoc-gen-mypy:
	poetry install --only=codegen --no-root

.PHONY: .venv
.venv: .venv/lib/python3.10/site-packages/sora_device_client.pth
.venv/lib/python3.10/site-packages/sora_device_client.pth: sora pyproject.toml poetry.toml poetry.lock
	poetry lock --check
	poetry install

.PHONY: clean
clean:
	git clean -ffidx -e Session.vim

lint:
	poetry run black --check .
	poetry run mypy

.PHONY: wheel
wheel: sora
	poetry build -f wheel
