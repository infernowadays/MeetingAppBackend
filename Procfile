web: daphne MeetingApp.asgi:application --port $PORT --bind 0.0.0.0
worker: python manage.py runworker realtime-event-sender -v2