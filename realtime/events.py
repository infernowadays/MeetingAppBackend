WEBSOCKET_DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class RequestEvent:
    def __init__(self, event, from_user, to_user, decision, created):
        self._type = "send_consumer_event_to_client"
        self._event = event
        self._from_user = from_user
        self._to_user = to_user
        self._decision = decision
        self._created = created

    @property
    def type(self):
        return self._type

    @property
    def event(self):
        return str(self._event)

    @property
    def from_user(self):
        return str(self._from_user)

    @property
    def to_user(self):
        return str(self._to_user)

    @property
    def decision(self):
        return str(self._decision)

    @property
    def created(self):
        return str(self._created)

    @property
    def properties_dict(self):
        return dict(
            type=self.type,
            event=self.event,
            from_user=self.from_user,
            to_user=self.to_user,
            decision=self.decision,
            created=self.created,
        )


class MessageEvent:
    def __init__(self, from_user, text, created, chat):
        self._type = "send_consumer_event_to_client"
        self._from_user = from_user
        self._text = text
        self._created = created
        self._chat = chat

    @property
    def type(self):
        return self._type

    @property
    def from_user(self):
        return str(self._from_user)

    @property
    def text(self):
        return self._text

    @property
    def created(self):
        return self._created.strftime(WEBSOCKET_DATE_TIME_FORMAT)

    @property
    def chat(self):
        return str(self._chat)

    @property
    def properties_dict(self):
        return dict(
            type=self.type,
            from_user=self.from_user,
            text=self.text,
            created=self.created,
            chat=self.chat,
        )
