SORA_API_REF := 72a98b24d4a63cf029ab039ddb1e961a04211c75

.PHONY: build
build: sora .venv

.PHONY: shell
shell: build
	poetry shell

sora: buf.gen.yaml
	buf generate buf.build/swift-nav/sora-api:$(SORA_API_REF)

.venv: sora pyproject.toml poetry.toml poetry.lock
	poetry install

.PHONY: clean
clean:
	git clean -ffidx -e Session.vim
