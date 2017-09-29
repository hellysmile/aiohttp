"""HTTP related errors."""

import asyncio


try:
    import ssl
except ImportError:  # pragma: no cover
    ssl = None


__all__ = (
    'ClientError',

    'ClientConnectionError',
    'ClientOSError', 'ClientConnectorError', 'ClientProxyConnectionError',
    'ClientConnectorSSLError', 'ClientConnectorCertificateError',

    'ServerConnectionError', 'ServerTimeoutError', 'ServerDisconnectedError',
    'ServerFingerprintMismatch',

    'ClientResponseError', 'ClientHttpProxyError',
    'WSServerHandshakeError', 'ContentTypeError',

    'ClientPayloadError', 'InvalidURL')


class ClientError(Exception):
    """Base class for client connection errors."""


class ClientResponseError(ClientError):
    """Connection error during reading response.

    :param request_info: instance of RequestInfo
    """

    def __init__(self, request_info, history, *,
                 code=0, message='', headers=None):
        self.request_info = request_info
        self.code = code
        self.message = message
        self.headers = headers
        self.history = history

        super().__init__("%s, message='%s'" % (code, message))


class ContentTypeError(ClientResponseError):
    """ContentType found is not valid."""


class WSServerHandshakeError(ClientResponseError):
    """websocket server handshake error."""


class ClientHttpProxyError(ClientResponseError):
    """HTTP proxy error.

    Raised in :class:`aiohttp.connector.TCPConnector` if
    proxy responds with status other than ``200 OK``
    on ``CONNECT`` request.
    """


class ClientConnectionError(ClientError):
    """Base class for client socket errors."""


class ClientOSError(ClientConnectionError, OSError):
    """OSError error."""


class ClientConnectorError(ClientOSError):
    """Client connector error.

    Raised in :class:`aiohttp.connector.TCPConnector` if
        connection to proxy can not be established.
    """
    def __init__(self, connection_key, os_error):
        self._conn_key = connection_key
        self._os_error = os_error
        super().__init__(os_error.errno, os_error.strerror)

    @property
    def os_error(self):
        return self._os_error

    @property
    def host(self):
        return self._conn_key.host

    @property
    def port(self):
        return self._conn_key.port

    @property
    def ssl(self):
        return self._conn_key.ssl

    def __str__(self):
        return ('Cannot connect to host {0.host}:{0.port} ssl:{0.ssl} [{1}]'
                .format(self, self.strerror))


class ClientProxyConnectionError(ClientConnectorError):
    """Proxy connection error.

    Raised in :class:`aiohttp.connector.TCPConnector` if
        connection to proxy can not be established.
    """


class ServerConnectionError(ClientConnectionError):
    """Server connection errors."""


class ServerDisconnectedError(ServerConnectionError):
    """Server disconnected."""

    def __init__(self, message=None):
        self.message = message


class ServerTimeoutError(ServerConnectionError, asyncio.TimeoutError):
    """Server timeout error."""


class ServerFingerprintMismatch(ServerConnectionError):
    """SSL certificate does not match expected fingerprint."""

    def __init__(self, expected, got, host, port):
        self.expected = expected
        self.got = got
        self.host = host
        self.port = port

    def __repr__(self):
        return '<{} expected={} got={} host={} port={}>'.format(
            self.__class__.__name__, self.expected, self.got,
            self.host, self.port)


class ClientPayloadError(ClientError):
    """Response payload error."""


class InvalidURL(ClientError, ValueError):
    """Invalid URL.

    URL used for fetching is malformed, e.g. it doesn't contains host
    part."""

    # Derive from ValueError for backward compatibility

    def __init__(self, url):
        super().__init__(url)

    @property
    def url(self):
        return self.args[0]

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.url)


if ssl is not None:
    certificate_errors = (ssl.CertificateError,)
    certificate_errors_bases = (ClientConnectorError, ssl.CertificateError,)

    ssl_errors = (ssl.SSLError,)
    ssl_error_bases = (ClientConnectorError, ssl.SSLError)
else:
    certificate_errors = tuple()
    certificate_errors_bases = (ClientConnectorError, ValueError,)

    ssl_errors = tuple()
    ssl_error_bases = (ClientConnectorError,)


class ClientConnectorSSLError(*ssl_error_bases):
    """Response ssl error."""


class ClientConnectorCertificateError(*certificate_errors_bases):
    """Response certificate error."""

    def __init__(self, connection_key, certificate_error):
        self._conn_key = connection_key
        self._certificate_error = certificate_error

    @property
    def certificate_error(self):
        return self._certificate_error

    @property
    def host(self):
        return self._conn_key.host

    @property
    def port(self):
        return self._conn_key.port

    @property
    def ssl(self):
        return self._conn_key.ssl

    def __str__(self):
        return ('Cannot connect to host {0.host}:{0.port} ssl:{0.ssl} '
                '[{0.certificate_error.__class__.__name__}: '
                '{0.certificate_error.args}]'.format(self))
