release: python manage.py migrate --noinput
web: daphne MeetingApp.asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2
worker: python manage.py runworker realtime-event-sender -v2