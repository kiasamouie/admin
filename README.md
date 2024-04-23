# Django & Next.js Authentication fullstack application

## Stack used
- Django and DRF for the backend
- Next.js and Tailwind on the frontend
- Wretch for API calls
- Djoser for authentication

## Setup

### With Docker

```shell
docker compose up -d --build
```

By default, the Django backend will be running on localhost:8000 and the frontend on localhost:3000. 

## Manual setup

```bash
git clone https://github.com/kiasamouie/admin.git && cd admin
```

Run the `setup.sh` script to handle dependencies installation on the backend and the frontend. 

```shell
chmod +x setup.sh
./setup.sh
```

To start the application, run the following commands. 

```bash
source venv/bin/activate
python manage.py runserver
```

The commands above will start the backend application. To start the frontend, run the following commands. 

```bash
cd frontend
npm run dev
```
