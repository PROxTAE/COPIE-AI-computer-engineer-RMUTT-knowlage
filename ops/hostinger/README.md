# Hostinger VPS deployment

Production hostname: https://tntproduction.tech

The deployment uses Next.js, FastAPI with CPU-only PyTorch, and Caddy for
automatic HTTPS. Only ports 80 and 443 are published. SQLite, Chroma,
embedding models, and HTTPS certificates persist in Docker volumes.

Source is installed at `/opt/copie` on the VPS. Keep `.env` outside version
control and restrict it to the server administrator (`chmod 600 .env`).
Development authentication is disabled in the production Compose file.

From `/opt/copie`:

```sh
docker compose --env-file .env -p copie -f ops/hostinger/docker-compose.yml up -d --build
docker compose --env-file .env -p copie -f ops/hostinger/docker-compose.yml ps
docker compose --env-file .env -p copie -f ops/hostinger/docker-compose.yml logs --tail=100
```

Check `https://tntproduction.tech/api/health` for `{"status":"ok"}`.
Google OAuth must allow `https://tntproduction.tech` as a JavaScript origin
in the Google Cloud OAuth client used by the project.

Back up the `copie_storage` volume before future migrations. Do not use
`docker compose down -v`: it removes persistent application data and certificates.
