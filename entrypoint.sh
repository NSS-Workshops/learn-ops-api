#!/bin/bash

set -e

export DJANGO_SETTINGS_MODULE="LearningPlatform.settings"

# Function to wait for PostgreSQL to be ready
wait_for_postgres() {
    echo "Waiting for PostgreSQL at $LEARN_OPS_HOST:$LEARN_OPS_PORT..."
    while ! pg_isready -h "$LEARN_OPS_HOST" -p "$LEARN_OPS_PORT" -U "$LEARN_OPS_USER"; do
        sleep 1
    done
    echo "PostgreSQL is ready!"
}

wait_for_postgres

# Generate socialaccount fixture with environment variables
echo "Creating socialaccount fixture..."
cat > ./LearningAPI/fixtures/socialaccount.json << EOF
[
    {
       "model": "sites.site",
       "pk": 1,
       "fields": {
          "domain": "learningplatform.com",
          "name": "Learning Platform"
       }
    },
    {
        "model": "socialaccount.socialapp",
        "pk": 1,
        "fields": {
            "provider": "github",
            "name": "Github",
            "client_id": "$LEARN_OPS_CLIENT_ID",
            "secret": "$LEARN_OPS_SECRET_KEY",
            "key": "",
            "sites": [
                1
            ]
        }
    }
]
EOF

# Generate superuser fixture with environment variables
echo "Creating superuser fixture..."
DJANGO_GENERATED_PASSWORD=$(python3 ./djangopass.py "$LEARN_OPS_SUPERUSER_PASSWORD")

cat > ./LearningAPI/fixtures/superuser.json << EOF
[
    {
        "model": "auth.user",
        "pk": 3,
        "fields": {
            "password": "$DJANGO_GENERATED_PASSWORD",
            "last_login": null,
            "is_superuser": true,
            "username": "$LEARN_OPS_SUPERUSER_NAME",
            "first_name": "Admina",
            "last_name": "Straytor",
            "email": "me@me.com",
            "is_staff": true,
            "is_active": true,
            "date_joined": "2023-03-17T03:03:13.265Z",
            "groups": [
                2
            ],
            "user_permissions": []
        }
    }
]
EOF

# Run migrations (always — safe to re-run, applies any new migrations)
echo "Running database migrations..."
python3 manage.py migrate

# If WIPE_DB=true, flush everything so fixtures will reload below
if [ "${WIPE_DB:-false}" = "true" ]; then
    echo "WIPE_DB=true — flushing database..."
    python3 manage.py flush --no-input
fi

# Only load fixtures when the DB is empty (no users exist yet)
USER_COUNT=$(python3 manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())" 2>/dev/null | tail -1 | tr -d '[:space:]')

if [ "$USER_COUNT" = "0" ]; then
    echo "Database is empty, loading fixture data..."
    python3 manage.py loaddata ./LearningAPI/fixtures/*.json
    echo "Fixture data loaded."
else
    echo "Database already has data ($USER_COUNT users) — skipping fixture load."
fi

# Clean up temporary fixture files
echo "Cleaning up temporary fixture files..."
rm -f ./LearningAPI/fixtures/socialaccount.json
rm -f ./LearningAPI/fixtures/superuser.json

echo "Database setup complete!"

# Hand off to whatever was given in CMD (or docker run args)
exec "$@"