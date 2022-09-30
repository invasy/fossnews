import asyncio
import logging
import re
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import final
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from aiohttp import ClientSession
from aiohttp_retry import RetryClient
from feedparser import FeedParserDict, parse as parse_feed

from .datetime import to_datetime
from .meta import Singleton
from .models import ContentType, Language, News, SourceType, Source


__all__ = (
    'Client',
    'SourceParsers',
)


log = logging.getLogger('fossnews.parser')

# Type aliases
Client = ClientSession | RetryClient
NewsParser = Callable[[Client, News], Awaitable[News]]
SourceParser = Callable[[Client, Source], Awaitable[list[News]]]
UrlPattern = re.Pattern[str]
NewsParserPattern = tuple[UrlPattern, NewsParser]
NewsParsersList = list[NewsParserPattern]


def urlclean(url: str) -> str:
    """
    Remove `UTM parameters`_ from URL.

    .. _UTM parameters: https://en.wikipedia.org/wiki/UTM_parameters

    :param url: URL to clean.
    :return: Cleaned URL without UTM parameters.
    """
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    query = {k: v for k, v in query.items() if not k.startswith('utm_')}
    parsed = parsed._replace(query=urlencode(query, doseq=True))
    return urlunparse(parsed)


@final
class NewsParsers(metaclass=Singleton):
    @classmethod
    async def _default(cls, client: Client, news: News) -> News:
        return news

    def __init__(self):
        self._parsers: NewsParsersList = []

    def register(self, pattern: str):
        pattern = re.compile(pattern)

        def wrapper(f: NewsParser) -> NewsParser:
            self._parsers.append((pattern, f))
            return f

        return wrapper

    async def parse(self, client: Client, news: News) -> News:
        """
        Find parser by URL and parse content as news.

        News URL matching time: O(n).

        :param client: `aiohttp` client session.
        :type client: :type t: :class:ClientSession or :class:RetryClient
        :param news: news to parse and update.
        :type news: :class:News
        :return: Updated news.
        :rtype: :class:News
        """
        parser = self._default

        for p in self._parsers:
            if p[0].match(news.url):
                parser = p[1]
                break

        return await parser(client, news)


@final
class SourceParsers(metaclass=Singleton):
    def __init__(self):
        self._parsers: dict[SourceType, SourceParser] = {}

    def register(self, t: SourceType):
        """
        Decorator to register parser for the source type.

        :param t: source type.
        :type t: :class:SourceType
        """
        def wrapper(f):
            self._parsers[t] = f
            return f

        return wrapper

    async def parse(self, client: Client, source: Source) -> list[News | BaseException]:
        """
        Parse news source and return list of news.

        :param client: `aiohttp` client session.
        :type client: :type t: :class:ClientSession or :class:RetryClient
        :param source: news source.
        :type source: :class:Source
        :return: list of news.
        """
        # Fetch news list from source
        news = await self._parsers[SourceType(source.type)](client, source)

        # Fetch missing news info if needed. Result is either updated news or exception (if any).
        news = await asyncio.gather(*[NewsParsers().parse(client, n) for n in news], return_exceptions=True)

        return list(news)


news_parsers = NewsParsers()
source_parsers = SourceParsers()


def decode_feed(feed: FeedParserDict) -> FeedParserDict:
    """
    Decode feed if it's not in UTF-8.

    :param feed: parsed feed.
    :type feed: :class:FeedParserDict
    :return: Decoded feed in UTF-8.
    :rtype: :class:FeedParserDict
    """
    encoding = feed.encoding

    if encoding and encoding != 'utf-8':
        def _decode(value: str | list | FeedParserDict) -> str | list | FeedParserDict:
            if isinstance(value, str):
                return value.encode(encoding=encoding, errors='ignore').decode(encoding='utf-8', errors='ignore')
            elif isinstance(value, list):
                return [_decode(v) for v in value]
            elif isinstance(value, FeedParserDict):
                for k, v in value.items():
                    value[k] = _decode(v)
            return value

        feed = _decode(feed)

    return feed


@source_parsers.register(SourceType.RSS)
async def feed_parser(client: Client, source: Source) -> list[News]:
    """
    Gather news from `RSS`_ or `Atom`_ feed.

    .. _RSS: https://www.rssboard.org/rss-specification
    .. _Atom: https://www.rfc-editor.org/rfc/rfc5023

    :param client: `aiohttp` client session.
    :param source: news source.
    :return: List of news from RSS/Atom feed.
    """
    async with client.get(source.url) as response:
        feed = decode_feed(parse_feed(await response.text()))

    for attr in ['title', 'language']:
        if attr not in feed:
            setattr(feed, attr, getattr(source, attr))

    news = [News(
        url=urlclean(entry.link),
        title=entry.title,
        author=', '.join(a.name for a in entry.get('authors', [])),
        summary=entry.summary,
        content=entry.get('content'),
        language=Language(feed.language),
        published_at=to_datetime(entry.published_parsed),
        gathered_at=datetime.utcnow(),
    ) for entry in feed.entries]

    return news


@news_parsers.register(r'^https://www\.techradar\.com/')
async def techradar(client: Client, news: News) -> News:
    news.content_type = ContentType.ARTICLE

    return news
