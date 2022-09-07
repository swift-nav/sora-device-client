SORA_API_REF := 3cabcf5e5addb862f01802c3c574740d6fbc70e5

.PHONY: build
build: sora .venv

.PHONY: shell
shell: build
	poetry shell

sora: buf.gen.yaml
	buf generate buf.build/swift-nav/sora-api:$(SORA_API_REF)

.venv: sora pyproject.toml poetry.toml poetry.lock
	poetry lock --check
	poetry install --no-root

.PHONY: clean
clean:
	git clean -ffidx -e Session.vim
