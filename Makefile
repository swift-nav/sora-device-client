SORA_API_REF=3674176de04d453b9d89dab9e316232a

.PHONY: build
build: sora .venv

sora: buf.gen.yaml
	buf generate buf.build/swift-nav/sora-api:$(SORA_API_REF)

.venv: sora sora_device_client pyproject.toml poetry.toml poetry.lock
	poetry install

.PHONY: clean
clean:
	git clean -ffidx -e Session.vim
