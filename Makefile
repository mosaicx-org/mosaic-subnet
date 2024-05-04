VERSION=$(shell git describe --tags --always)
IMAGE=mos4ic/mosaic-subnet

.PHONY: docker-build
docker-build:
	docker build -t $(IMAGE):$(VERSION) .

.PHONY: docker-push
docker-push:
	docker push $(IMAGE):$(VERSION)

.PHONY: docker-push-latest
docker-push:
	docker tag $(IMAGE):$(VERSION) $(IMAGE):latest
	docker push $(IMAGE):latest