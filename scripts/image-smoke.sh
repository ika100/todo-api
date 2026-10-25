#!/usr/bin/env bash
# Start the local image like Kubernetes would (read-only root, /tmp tmpfs) and probe /health.
# /ready may fail when no database is reachable; that is reported, not fatal.
set -u
name=todo-api-smoke
docker rm -f "$name" >/dev/null 2>&1
docker run -d --name "$name" --read-only --tmpfs /tmp -e DATABASE_URL=postgresql://smoke:smoke@127.0.0.1:5432/smoke -p 18080:8080 todo-api:scan >/dev/null || exit 1
rc=1
for _ in $(seq 1 20); do
  if curl -fsS http://localhost:18080/health; then rc=0; echo; break; fi
  sleep 1
done
echo "ready: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:18080/ready)"
echo "uid: $(docker exec "$name" id -u)"
[ $rc -ne 0 ] && docker logs "$name" 2>&1 | tail -20
docker rm -f "$name" >/dev/null 2>&1
exit $rc
