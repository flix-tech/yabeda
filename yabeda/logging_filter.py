from logging import Filter


class PingFilter(Filter):
    def filter(self, record):
        return not record.getMessage().endswith('"GET /ping HTTP/1.1" 200 -')
