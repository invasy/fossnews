import asyncio
import logging
from datetime import datetime
from traceback import format_exception

import spacy
from aiohttp import ClientTimeout, TCPConnector
from aiohttp_retry import RetryClient, FibonacciRetry
from asgiref.sync import async_to_sync, sync_to_async
from celery import shared_task
from dynamic_preferences.registries import global_preferences_registry

from .models import GatheringResult, News, Source
from .parsers import Client, SourceParsers


log = logging.getLogger('fossnews.gatherer')
preferences = global_preferences_registry.manager()
source_parsers = SourceParsers()
# nlp = dict(
#     en=spacy.load('en_core_web_trf'),
#     ru=spacy.load('ru_core_news_lg'),
# )


async def filter_news(news: News) -> bool:
    return not any([
        await News.objects.filter(url=news.url).aexists(),  # Filter duplicates
        # TODO: add filters
    ])


async def gather_from_source(client: Client, source: Source) -> GatheringResult:
    log.info('Started news gathering from %s', source.title)

    result = GatheringResult(source=source, started_at=datetime.utcnow())
    await sync_to_async(result.save)()

    try:
        news = await source_parsers.parse(client, source)
        result.total_count = len(news)
        errors = [''.join(format_exception(e)) for e in news if isinstance(e, BaseException)]
        result.errors_count = len(errors)
        result.errors = '\n'.join(errors)
        news = [n for n in news if isinstance(n, News) and await filter_news(n)]
        result.filtered_count = result.total_count - result.errors_count - len(news)
        for n in news:
            n.gathering = result
        result.saved_count = len(await News.objects.abulk_create(news))
    except Exception as e:  # Report all exceptions (if any) in the task result
        result.errors_count += 1
        result.errors = ''.join(format_exception(e))

    result.finished_at = datetime.utcnow()
    await sync_to_async(result.save)()

    log.info('Finished news gathering from %s', source.title)

    return result


async def agather(*args, **kwargs) -> list[dict]:
    """
    Gather news from selected sources asynchronously.

    :param args: Source filter args.
    :param kwargs: Source filter kwargs.
    :return: List of gathering results by source.
    """
    client_args = dict(
        connector=TCPConnector(limit=await preferences.aget('gatherer.connection_limit')),
        timeout=ClientTimeout(total=await preferences.aget('gatherer.connection_timeout')),
        retry_options=FibonacciRetry(attempts=await preferences.aget('gatherer.connection_retries')),
        raise_for_status=True,
        headers={
            'User-Agent': await preferences.aget('gatherer.user_agent'),
        },
    )

    async with RetryClient(**client_args) as client:
        tasks = [gather_from_source(client, source) async for source in Source.objects.filter(*args, **kwargs)]
        return [r.to_dict() for r in await asyncio.gather(*tasks)]


@shared_task(name='gather')
def gather(*args, **kwargs):
    return async_to_sync(agather)(*args, **kwargs)
