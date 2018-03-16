import aioredis

from objects.logger import Logger


DEFAULT_REDIS_PORT = 6379

logger = Logger.get_logger()

class RedisDB:

    def __init__(self):
        self.connection = None

    async def connect(self, **kwargs):
        if self.connection is not None and not self.connection.closed:
            logger.info(f'Warning: can\'t establish new connection to redis, connection already exists: {self.connection.address}')
            return

        port = kwargs.pop('port', DEFAULT_REDIS_PORT) or DEFAULT_REDIS_PORT
        password = kwargs.pop('password', None) or None

        self.connection = await aioredis.create_connection(
            ('localhost', port), password=password)

    async def reconnect(self):
        self.connection = await aioredis.create_connection(
            self.connection.address)

    def disconnect(self):
        if self.connection is None:
            logger.info('Warning: can\'t close connection to redis, doesn\'t exist')
            return

        self.connection.close()

    async def get(self, key, default=None):
        if not await self.exists(key):
            return default
        return await self.execute('GET', key)

    async def set(self, key, value, *args):
        return await self.execute('SET', key, value, *args)

    async def exists(self, *values):
        return await self.execute('EXISTS', *values) == len(values)

    async def get_db_size(self):
        return await self.execute('DBSIZE')

    async def execute(self, command, *args):
        if self.connection is None or self.connection.closed:
            logger.debug('Connection to redis db closed. Trying to reconnect ...')
            try:
                await self.reconnect()
            except Exception:
                logger.info(f'Could not reconnect to redis db. Command {command} failed')
                return

        value = await self.connection.execute(command, *args)

        return self.decode_value(value)

    def decode_value(self, value):
        if type(value) is list:
            return [self.decode_value(v) for v in value]
        elif type(value) is bytes:
            return value.decode()

        return value