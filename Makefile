.PHONY: grpc
grpc: sora

	buf generate buf.build/swift-nav/sora-api
sora:

.PHONY: clean
clean:
	git clean -ffidx
