import time
import functools

from django.db import connection, reset_queries


def debugger_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print('func: ', func.__name__)
        reset_queries()

        start_time = time.time()

        start_queries = len(connection.queries)
        result = func(*args, **kwargs)
        for query in connection.queries:
            print(query)

        end_queries = len(connection.queries)
        print('queries:', end_queries - start_queries)

        print(time.time() - start_time)
        return result

    return wrapper

def ajax_required(f):
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        return f(request, *args, **kwargs)
    return wrap
