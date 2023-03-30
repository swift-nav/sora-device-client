include .api-version

.ONESHELL:
.SHELLFLAGS=-e -c

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

lint: .venv
	poetry run black --check .
	poetry run mypy
	find sora_device_client -name '*.py' \
		| xargs grep -P --files-without-match '(?s)^# Copyright' \
		| (
			set +x
			FILES=$$(cat)
			if [ "$${FILES}" != "" ]; then
				echo "Files without copyright notice found!" 1>&2
				echo "$${FILES}" 1>&2
				exit 1
			else
				echo "All files include copyright notice!" 1>&2
			fi
		)

.PHONY: wheel
wheel: sora
	poetry build -f wheel
