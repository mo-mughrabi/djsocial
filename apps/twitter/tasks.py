# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime

from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings
from celery.utils.log import get_task_logger
from django.db.models import Q, Count
from pytz import utc
from django.utils import timezone

from apps.twitter.models import Order, ScheduleOrder
import tweepy
from tweepy import OAuthHandler, Cursor
from models import Twitter


# setup logger
logger = get_task_logger(__name__)


def get_diff(list1, list2):
    """Outputs objects which are in list1 but not list 2"""
    return list(set(list1).difference(set(list2)))


@periodic_task(run_every=crontab(minute="*/1"))
def process_scheduled_orders():
    """ process_scheduled_orders """
    logger.debug('process_scheduled_orders is starting up')
    delta_time = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(hours=1)
    delta_time = timezone.localtime(delta_time, timezone.get_current_timezone())
    auth = OAuthHandler(getattr(settings, 'TWITTER_CONSUMER_KEY'), getattr(settings, 'TWITTER_CONSUMER_SECRET'))

    for order in ScheduleOrder.objects.filter(
                    Q(Q(last_run__lte=delta_time) | Q(last_run__isnull=True)) & Q(run_once=False)):
        logger.debug('Order details: {}'.format(order.id))
        auth.set_access_token(order.user.access_token, order.user.secret_key)
        api = tweepy.API(auth)
        me = api.me()
        # black listed words / will be discarded when retweeting content or fav
        black_listed_words = ["RT", u"♺"]
        """
        this section for retweet or favoriate from watched user
        """
        if order.func in ('retweet_watch', 'favorite_watch'):
            # the hourly runs
            for user in order.args:
                last_id = None
                for tweet in Cursor(api.user_timeline, screen_name=user, include_rts=False,
                                    since_id=order.data.get(user, '')).items():
                    if last_id is None:
                        last_id = tweet.id
                    Order.objects.create(user=order.user, func=order.kwargs['func'], args=[tweet.id, ],
                                         schedule_order=order,
                                         kwargs={
                                             'func': order.kwargs['func'],
                                             'tweet': tweet.text.encode('utf-8'),
                                             'tweet_id': tweet.id,
                                             'source_url': tweet.source_url,
                                             'created_at': tweet.created_at,
                                             'screen_name': tweet.author.screen_name.encode('utf-8')})
                order.data[user] = last_id or order.data[user]
                order.last_run = datetime.datetime.utcnow().replace(tzinfo=utc)
                order.save()
        """
        this section for retweet or favoriate from searched keyword
        """
        if order.func in ('retweet_search', 'favorite_search'):
            # the hourly runs
            last_id = None
            logger.debug('Search hashtag: #{}'.format(order.args[0]))
            # for tweet in Cursor(api.search, q='#{}'.format(order.args[1]),
            #                     since_id=order.data['last_id']).items():
            timeline = []
            if 'last_id' in order.data:
                for tweet in Cursor(api.search, q=u'{}'.format(order.args[0]), result_type='popular',
                                    since_id=order.data['last_id']).items():
                    timeline.append(tweet)
            else:
                for tweet in Cursor(api.search, q=u'{}'.format(order.args[0]), result_type='popular').items(10):
                    timeline.append(tweet)

            timeline = filter(lambda status: status.text[0] != "@", timeline)
            timeline = filter(lambda status: not any(word in status.text.split() for word in black_listed_words),
                              timeline)
            # exclude self
            timeline = filter(lambda status: status.author.id != me.id, timeline)
            logger.info('TASK DETAILS: %s - %s' % (order, order.kwargs))
            for tweet in timeline:
                if last_id is None:
                    last_id = tweet.id

                Order.objects.create(user=order.user, func=order.kwargs['func'], args=[tweet.id, ],
                                     schedule_order=order,
                                     kwargs={
                                         'func': order.kwargs['func'],
                                         'tweet': tweet.text,
                                         'tweet_id': tweet.id,
                                         'source_url': tweet.source_url,
                                         'created_at': tweet.created_at,
                                         'screen_name': tweet.author.screen_name})

            order.data['last_id'] = last_id or order.data.get('last_id', '')
            order.last_run = datetime.datetime.utcnow().replace(tzinfo=utc)
            order.save()

        if order.func in ('follow', 'unfollow'):
            # if user is first timer

            follower_ids = []
            screen_names = {}
            try:
                for follower in tweepy.Cursor(api.followers).items():
                    follower_ids.append(follower.id)
                    screen_names.update({follower.id: follower.screen_name})

                friend_ids = []
                for friend in tweepy.Cursor(api.friends).items():
                    friend_ids.append(friend.id)
                    screen_names.update({friend.id: friend.screen_name})
            except tweepy.TweepError as e:
                order.last_run = datetime.datetime.utcnow().replace(tzinfo=utc)
                order.save()
                continue

            if order.kwargs['func'] == 'follow':
                follow_list = get_diff(follower_ids, friend_ids)

                for follower in follow_list:
                    Order.objects.create(user=order.user, func=order.kwargs['func'], args=[follower, ],
                                         schedule_order=order,
                                         kwargs={
                                             'func': order.kwargs['func'],
                                             'screen_name': screen_names[follower],
                                             'user_id': follower})

            if order.kwargs['func'] == 'unfollow':
                unfollow_list = get_diff(friend_ids, follower_ids)

                for follower in unfollow_list:
                    Order.objects.create(user=order.user, func=order.kwargs['func'], args=[follower, ],
                                         schedule_order=order,
                                         kwargs={
                                             'func': order.kwargs['func'],
                                             'screen_name': screen_names[follower],
                                             'user_id': follower})

            order.last_run = datetime.datetime.utcnow().replace(tzinfo=utc)
            order.save()

    logger.info('process_scheduled_orders ended successfully')
    return u'Success'


@periodic_task(run_every=crontab(minute="*/1"))
def provision_orders():
    """ provision_orders """
    logger.info('provision_orders is starting up')
    auth = OAuthHandler(getattr(settings, 'TWITTER_CONSUMER_KEY'), getattr(settings, 'TWITTER_CONSUMER_SECRET'))

    # first we get all the pending orders for a given user (users with pending orders > 0)
    for pending in Order.objects.values('user').filter(status=Order.PENDING).annotate(user_count=Count('user')).filter(
            user_count__gt=0):
        # get user threshold
        user_threshold = Twitter.objects.get(pk=pending.get('user')).user.threshold
        threshold = user_threshold / 24  # per hour
        now = timezone.localtime(timezone.now(), timezone.get_current_timezone())
        # get user hourly usage / return total number of executed commands in the given hour of the day
        # if hours do not exceed user threshold we continue
        hour_usage = Order.objects.filter(executed_at__year=now.year, executed_at__month=now.month,
                                          executed_at__day=now.day, executed_at__hour=now.hour,
                                          status__in=(Order.COMPLETED, Order.FAILED), user_id=pending.get('user'))

        hour_usage = hour_usage.count()
        logger.info('provision_orders: user hourly usage: {0} vs threshold {1}'.format(hour_usage, threshold))

        # skip user as he/she reached limit of hourly usage
        if hour_usage > threshold:
            continue
        for order in Order.objects.filter(status=Order.PENDING, user_id=pending.get('user'))[:1]:
            # only execute one command at a time
            try:
                auth.set_access_token(order.user.access_token, order.user.secret_key)
                api = tweepy.API(auth)
                if order.kwargs['func'] == 'retweet':
                    api.retweet(order.kwargs['tweet_id'])
                if order.kwargs['func'] == 'favorite':
                    api.create_favorite(order.kwargs['tweet_id'])
                if order.kwargs['func'] == 'follow':
                    api.create_friendship(order.kwargs['user_id'])
                if order.kwargs['func'] == 'unfollow':
                    api.destroy_friendship(order.kwargs['user_id'])
                order.status = order.COMPLETED
            except tweepy.TweepError as e:
                #TODO: Handle general erros as fail and RATE LIMIT error for retry
                order.status = order.FAILED
                order.result = 'Exception: %s' % str(e)
            order.executed_at = datetime.datetime.utcnow().replace(tzinfo=utc)
            order.save()

    logger.info('provision_orders ended successfully')
    return u'Success'
