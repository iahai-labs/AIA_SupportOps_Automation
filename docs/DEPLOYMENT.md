# Production Deployment

## Public URL
`https://ai.iradhd.ir/supportops/`

## Topology

```text
Cloudflare / HTTPS
        ↓
Host Nginx reverse proxy
        ↓
127.0.0.1:8003
        ↓
FastAPI container
        ↓
PostgreSQL container
```

## Container behavior

The production Compose configuration:

- builds from `Dockerfile.prod`
- runs the application as a non-root user
- binds the app to `127.0.0.1:8003`
- keeps PostgreSQL unexposed
- includes application and database health checks
- enables `ROOT_PATH=/supportops`
- enables demo safe mode
- disables external AI and outbound automation by default

## Required production secret

Create `.env.prod` locally on the server and keep it out of Git:

```text
POSTGRES_PASSWORD=<strong-random-password>
AI_API_KEY=
N8N_WEBHOOK_URL=
N8N_WEBHOOK_SECRET=
```

## Start

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

## Health verification

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
curl -i http://127.0.0.1:8003/health
```

## Nginx subpath

```nginx
location = /supportops {
    return 301 /supportops/;
}

location = /supportops/ {
    return 302 /supportops/demo;
}

location /supportops/ {
    proxy_pass http://127.0.0.1:8003;
    proxy_http_version 1.1;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Prefix /supportops;
}
```

The missing trailing slash on `proxy_pass` is intentional because FastAPI is configured with `ROOT_PATH=/supportops`.

## Public smoke test

Verify:

```text
/supportops/demo
/supportops/static/demo/style.css
/supportops/static/demo/app.js
/supportops/docs
/supportops/openapi.json
```

Then complete the UI workflow:

1. seed demo knowledge
2. create ticket
3. retrieve knowledge
4. generate draft
5. approve or reject
6. verify audit timeline
