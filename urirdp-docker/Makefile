.PHONY: test docker-up docker-test test-rdp-real call down

test:
	./scripts/test-local.sh

docker-up:
	docker compose up --build urirdp

docker-test:
	./scripts/test-docker.sh

test-rdp-real:
	./scripts/test-rdp-real.sh

call:
	./scripts/call-http.sh

down:
	docker compose down -v
	docker compose -f docker-compose.rdp-e2e.yml down -v 2>/dev/null || true
