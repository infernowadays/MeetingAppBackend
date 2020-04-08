web: uvicorn MeetingApp:app --port=${PORT:-5000}
worker: python manage.py runworker realtime-event-sender -v2