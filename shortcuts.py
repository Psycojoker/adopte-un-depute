from flask import abort


def get_object_or_404(database_object, *args, **kwargs):
    database_object = database_object.collection.find_one(*args, **kwargs)
    if not database_object:
        abort(404)
    return database_object
