from channels.db import database_sync_to_async


def construct_group_name_from_uid(uid):
    return 'chat_%s' % str(uid)
