VERSION=$(shell git describe --tags --always)
IMAGE=mos4ic/mosaic-subnet

.PHONY: docker-build
docker-build:
	docker build -t $(IMAGE):$(VERSION) .

.PHONY: docker-push
docker-push:
	docker tag $(IMAGE):$(VERSION) $(IMAGE):latest
	docker push $(IMAGE):$(VERSION)
	docker push $(IMAGE):latest