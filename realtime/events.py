class CreatedRequestEvent:
    def __init__(self, sender_id):
        self._type = "created_event_request"
        self._sender_id = sender_id

    @property
    def type(self):
        return self._type

    @property
    def sender_id(self):
        return str(self._sender_id)

    @property
    def properties_dict(self):
        return dict(
            type=self.type,
            sender_id=self.sender_id,
        )
