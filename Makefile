SORA_API_REF=3674176de04d453b9d89dab9e316232a

.PHONY: grpc
grpc: sora

sora:
	buf generate buf.build/swift-nav/sora-api:$(SORA_API_REF)

.PHONY: clean
clean:
	git clean -ffidx
