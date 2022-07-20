.PHONY: grpc
grpc: sora_api

sora_api:
	buf generate buf.build/swift-nav/sora-api

.PHONY: clean
clean:
	git clean -ffidx
