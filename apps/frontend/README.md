# frontend

Vite + React + TypeScript UI for the Code Critic orchestrator.

## Run locally

```bash
cd apps/frontend
npm install
npm run dev          # http://localhost:5173, proxies /api → orchestrator
npm test             # vitest + RTL
npm run lint         # eslint
npm run format:check # prettier
```

## Run in Docker

The Dockerfile builds with `node:20-alpine` and serves the static bundle from
`nginx:1.27-alpine`. nginx proxies `/api/` to the `orchestrator` service in
`docker-compose.yml`.
