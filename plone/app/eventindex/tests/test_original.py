from DateTime import DateTime
from datetime import datetime
from plone.app.eventindex import EventIndex
from pytz import timezone

import unittest2 as unittest


# Handy when debugging timezoned events:
def utcify(o):
    if isinstance(o, DateTime):
        o = o.utcdatetime()
    return o.utctimetuple()


class TestOb(object):

    def __init__(self, name, start, end, recurrence):
        self.name = name
        self.start = start
        self.end = end
        self.recurrence = recurrence


class EventIndexTests(unittest.TestCase):

    def test_simplelookup(self):
        test_objects = {
            1: TestOb('a', datetime(2011, 4, 5, 12, 0), datetime(2011, 4, 5, 13, 0), None),
            2: TestOb('b', datetime(2011, 4, 6, 12, 0), datetime(2011, 4, 6, 13, 0), None),
            3: TestOb('c', datetime(2011, 4, 7, 12, 0), datetime(2011, 4, 7, 13, 0), None),
            4: TestOb('d', datetime(2011, 4, 7, 14, 0), datetime(2011, 4, 7, 15, 0), None),
            5: TestOb('e', datetime(2011, 4, 7, 12, 0), datetime(2011, 4, 7, 16, 0), None),
        }

        index = EventIndex('event', extra={'start_attr': '', 'end_attr': '', 'recurrence_attr': ''})
        for uid, ob in test_objects.items():
            index.index_object(uid, ob)

        # Return all
        res = index._apply_index({})
        self.assertEqual(len(res[0]), 5)

        # Return one
        res = index._apply_index({'event': {'start': datetime(2011, 4, 5, 12, 0),
                                            'end': datetime(2011, 4, 5, 13, 0)}})
        self.assertEqual(len(res[0]), 1)
        self.assertTrue(1 in res[0])

        # Get a bunch this day:
        res = index._apply_index({'event': {'start': datetime(2011, 4, 7, 0, 0),
                                            'end': datetime(2011, 4, 8, 0, 0)}})
        self.assertEqual(len(res[0]), 3)
        self.assertTrue(3 in res[0])
        self.assertTrue(4 in res[0])
        self.assertTrue(5 in res[0])

        # Get two out of the three during this day.
        res = index._apply_index({'event': {'start': datetime(2011, 4, 7, 14, 0),
                                            'end': datetime(2011, 4, 7, 15, 0)}})
        self.assertEqual(len(res[0]), 2)
        self.assertTrue(4 in res[0])
        self.assertTrue(5 in res[0])

        # Start date but no end date:
        res = index._apply_index({'event': {'start': datetime(2011, 4, 6, 20, 0),}})
        self.assertEqual(len(res[0]), 3)
        self.assertTrue(3 in res[0])
        self.assertTrue(4 in res[0])
        self.assertTrue(5 in res[0])

        # End date but no start date:
        res = index._apply_index({'event': {'end': datetime(2011, 4, 6, 20, 0),}})
        self.assertEqual(len(res[0]), 2)
        self.assertTrue(1 in res[0])
        self.assertTrue(2 in res[0])

    def test_DateTime(self):
        test_objects = {
            1: TestOb('a', DateTime('2011/4/5 12:00 UTC'), DateTime('2011/4/5 13:00 UTC'), None),
            2: TestOb('b', DateTime('2011/4/6 12:00 UTC'), DateTime('2011/4/6 13:00 UTC'), None),
            3: TestOb('c', DateTime('2011/4/7 12:00 UTC'), DateTime('2011/4/7 13:00 UTC'), None),
            4: TestOb('d', DateTime('2011/4/7 14:00 UTC'), DateTime('2011/4/7 15:00 UTC'), None),
            5: TestOb('e', DateTime('2011/4/7 12:00 UTC'), DateTime('2011/4/7 16:00 UTC'), None),
        }

        index = EventIndex('event', extra={'start_attr': '', 'end_attr': '', 'recurrence_attr': ''})
        for uid, ob in test_objects.items():
            index.index_object(uid, ob)

        # Return all
        res = index._apply_index({})
        self.assertEqual(len(res[0]), 5)

        # Return one
        res = index._apply_index({'event': {'start': DateTime('2011/4/5 12:00 UTC'),
                                            'end': DateTime('2011/4/5 13:00 UTC')}})
        self.assertEqual(len(res[0]), 1)
        self.assertTrue(1 in res[0])

        # Get a bunch this day:
        res = index._apply_index({'event': {'start': DateTime('2011/4/7 00:00 UTC'),
                                            'end': DateTime('2011/4/8 00:00 UTC')}})
        self.assertEqual(len(res[0]), 3)
        self.assertTrue(3 in res[0])
        self.assertTrue(4 in res[0])
        self.assertTrue(5 in res[0])

        # Get two out of the three during this day.
        res = index._apply_index({'event': {'start': DateTime('2011/4/7 14:00 UTC'),
                                            'end': DateTime('2011/4/7 15:00 UTC')}})
        self.assertEqual(len(res[0]), 2)
        self.assertTrue(4 in res[0])
        self.assertTrue(5 in res[0])

        # Start date but no end date:
        res = index._apply_index({'event': {'start': DateTime('2011/4/6 20:00 UTC'),}})
        self.assertEqual(len(res[0]), 3)
        self.assertTrue(3 in res[0])
        self.assertTrue(4 in res[0])
        self.assertTrue(5 in res[0])

        # End date but no start date:
        res = index._apply_index({'event': {'end': DateTime('2011/4/6 20:00 UTC'),}})
        self.assertEqual(len(res[0]), 2)
        self.assertTrue(1 in res[0])
        self.assertTrue(2 in res[0])

    def test_mixed_data(self):
        # DateTime and datetime, different timezones, no timezones.
        eastern = timezone('US/Eastern')
        paris = timezone('Europe/Paris')
        test_objects = {
            1: TestOb('a', datetime(2011, 4, 5, 12, 0), datetime(2011, 4, 5, 13, 0), None),
            2: TestOb('b', eastern.localize(datetime(2011, 4, 6, 8, 0)),
                      eastern.localize(datetime(2011, 4, 6, 9, 0)), None),
            3: TestOb('c', paris.localize(datetime(2011, 4, 7, 14, 0)),
                      paris.localize(datetime(2011, 4, 7, 15, 0)), None),
            4: TestOb('d', DateTime('2011/4/7 14:00 UTC'), DateTime('2011/4/7 15:00 UTC'), None),
            5: TestOb('e', DateTime('2011/4/7 5:00 PST'), DateTime('2011/4/7 9:00 PST'), None),
        }

        index = EventIndex('event')
        for uid, ob in test_objects.items():
            index.index_object(uid, ob)

        # Return all
        res = index._apply_index({})
        self.assertEqual(len(res[0]), 5)

        # Return one
        res = index._apply_index({'event': {'start': datetime(2011, 4, 5, 12, 0),
                                            'end': datetime(2011, 4, 5, 13, 0)}})
        self.assertEqual(len(res[0]), 1)
        self.assertTrue(1 in res[0])

        # Get a bunch this day with DateTime
        res = index._apply_index({'event': {'start': DateTime('2011/4/7 00:00 UTC'),
                                            'end': DateTime('2011/4/8 00:00 UTC')}})
        self.assertEqual(len(res[0]), 3)
        self.assertTrue(3 in res[0])
        self.assertTrue(4 in res[0])
        self.assertTrue(5 in res[0])

        # Get two out of the three with a timezoned query:
        res = index._apply_index({'event': {'start': eastern.localize(datetime(2011, 4, 7, 10, 0)),
                                            'end': eastern.localize(datetime(2011, 4, 7, 11, 0))}})
        self.assertEqual(len(res[0]), 2)
        self.assertTrue(4 in res[0])
        self.assertTrue(5 in res[0])

        # Start date but no end date:
        res = index._apply_index({'event': {'start': datetime(2011, 4, 6, 20, 0),}})
        self.assertEqual(len(res[0]), 3)
        self.assertTrue(3 in res[0])
        self.assertTrue(4 in res[0])
        self.assertTrue(5 in res[0])

        # End date but no start date:
        res = index._apply_index({'event': {'end': datetime(2011, 4, 6, 20, 0),}})
        self.assertEqual(len(res[0]), 2)
        self.assertTrue(1 in res[0])
        self.assertTrue(2 in res[0])

    def test_unindex(self):
        test_objects = {
            1: TestOb('a', datetime(2011, 4, 5, 12, 0), datetime(2011, 4, 5, 13, 0), None),
            2: TestOb('b', datetime(2011, 4, 6, 12, 0), datetime(2011, 4, 6, 13, 0), None),
            3: TestOb('c', datetime(2011, 4, 7, 12, 0), datetime(2011, 4, 7, 13, 0), None),
            4: TestOb('d', datetime(2011, 4, 7, 14, 0), datetime(2011, 4, 7, 15, 0), None),
            5: TestOb('e', datetime(2011, 4, 7, 12, 0), datetime(2011, 4, 7, 16, 0), None),
        }

        index = EventIndex('event', extra={'start_attr': '', 'end_attr': '', 'recurrence_attr': ''})
        for uid, ob in test_objects.items():
            index.index_object(uid, ob)

        for uid, ob in test_objects.items():
            index.unindex_object(uid)

        # Make sure all indexes are clean (yes, this tests internal state)
        self.assertEqual(len(index._end2uid), 0)
        self.assertEqual(len(index._start2uid), 0)
        self.assertEqual(len(index._uid2duration), 0)
        self.assertEqual(len(index._uid2end), 0)
        self.assertEqual(len(index._uid2recurrence), 0)
        self.assertEqual(len(index._uid2start), 0)

    def test_basic_recurrence(self):
        test_objects = {
            1: TestOb('a', datetime(2011, 4, 5, 12, 0), datetime(2011, 4, 5, 13, 0), 'RRULE:FREQ=DAILY;INTERVAL=10;COUNT=5'),
        }

        index = EventIndex('event', extra={'start_attr': '', 'end_attr': '', 'recurrence_attr': ''})
        for uid, ob in test_objects.items():
            index.index_object(uid, ob)

        # Return all
        res = index._apply_index({})
        self.assertTrue(1 in res[0])

        # Return one
        res = index._apply_index({'event': {'start': datetime(2011, 4, 5, 12, 0),
                                            'end': datetime(2011, 4, 5, 13, 0)}})
        self.assertEqual(len(res[0]), 1)
        self.assertTrue(1 in res[0])

        # Same one, twenty days later
        res = index._apply_index({'event': {'start': datetime(2011, 4, 25, 12, 0),
                                            'end': datetime(2011, 4, 25, 13, 0)}})
        self.assertEqual(len(res[0]), 1)
        self.assertTrue(1 in res[0])

    def test_recurrence_with_timezone(self):
        helsinki = timezone('Europe/Helsinki')

        index = EventIndex('event')
        index.index_object(1, TestOb(
            name='a',
            start=helsinki.localize(datetime(2011, 10, 3, 15, 40)),
            end=helsinki.localize(datetime(2011, 10, 3, 18, 34)),
            recurrence='RRULE:FREQ=DAILY;INTERVAL=10;COUNT=5'))

        res = index._apply_index({
            'event': {
                'start': helsinki.localize(datetime(2011, 10, 3)),
                'end': helsinki.localize(datetime(2011, 12, 10)),
            }
        })
        self.assertEqual(len(res[0]), 1)
        self.assertTrue(1 in res[0])

    def test_mixed_timezones(self):
        helsinki = timezone('Europe/Helsinki')

        index = EventIndex('event')
        index.index_object(1, TestOb(
            name='a',
            start=helsinki.localize(datetime(2011, 10, 3, 15, 40)),
            end=helsinki.localize(datetime(2011, 10, 3, 18, 34)),
            recurrence='\r\n'.join([
                'RRULE:FREQ=WEEKLY;BYDAY=MO;COUNT=10',
                'EXDATE:20120220T000000',
                'RDATE:20120120T000000'])))

        res = index._apply_index({
            'event': {
                'start': helsinki.localize(datetime(2011, 10, 3)),
                'end': helsinki.localize(datetime(2011, 10, 6)),
            }
        })
        self.assertEqual(len(res[0]), 1)
        self.assertTrue(1 in res[0])

        index = EventIndex('event')
        index.index_object(2, TestOb(
            name='b',
            start=datetime(2011, 10, 3, 15, 40),
            end=datetime(2011, 10, 3, 18, 34),
            recurrence='\r\n'.join([
                'RRULE:FREQ=WEEKLY;BYDAY=MO;COUNT=10',
                'EXDATE:20120220T000000Z',
                'RDATE:20120120T000000Z'])))

        res = index._apply_index({
            'event': {
                'start': helsinki.localize(datetime(2011, 10, 3)),
                'end': helsinki.localize(datetime(2011, 10, 6)),
            }
        })
        self.assertEqual(len(res[0]), 1)
        self.assertTrue(2 in res[0])

    def test_infinite_recurrence(self):
        helsinki = timezone('Europe/Helsinki')

        # Index an event that goes on forever. All events being infinitely
        # recurring is a special case, so we need to test for this.
        index = EventIndex('event')
        index.index_object(1, TestOb(
            name='a',
            start=helsinki.localize(datetime(2011, 10, 3, 15, 40)),
            end=helsinki.localize(datetime(2011, 10, 3, 18, 34)),
            recurrence='RRULE:FREQ=DAILY;INTERVAL=100'))

        # And now query for it with no end.
        # If the index does not handle this case specially, we'd
        # generate recurrences until we ran out of memory.
        res = index._apply_index({
            'event': {
                'start': helsinki.localize(datetime(2011, 10, 3)),
            }
        })
        self.assertEqual(len(res[0]), 1)
        self.assertTrue(1 in res[0])

        # And we also need to test for having events that do end together
        # with infinitely recurring events as well.
        index.index_object(2, TestOb(
            name='a',
            start=helsinki.localize(datetime(2011, 10, 3, 15, 40)),
            end=helsinki.localize(datetime(2011, 10, 3, 18, 34)),
            recurrence='RRULE:FREQ=DAILY;INTERVAL=10;COUNT=5'))

        res = index._apply_index({
            'event': {
                'start': helsinki.localize(datetime(2011, 10, 3)),
            }
        })
        self.assertEqual(len(res[0]), 2)
        self.assertTrue(1 in res[0])
        self.assertTrue(2 in res[0])

        # Now search after the ending event ends, and we'll only get the
        # neverending recurrence back.

        res = index._apply_index({
            'event': {
                'start': helsinki.localize(datetime(2012, 10, 3)),
            }
        })
        self.assertEqual(len(res[0]), 1)
        self.assertTrue(1 in res[0])

    def test_recurrence_exdate(self):
        # Turns out that if you have EXDATE and RDATE, rulestr() will return a
        # ruleset, which has a different interface.
        helsinki = timezone('Europe/Helsinki')

        # Index an event that goes on forever. All events being infinitely
        # recurring is a special case, so we need to test for this.
        index = EventIndex('event')
        index.index_object(1, TestOb(
            name='a',
            start=helsinki.localize(datetime(2011, 10, 3, 15, 40)),
            end=helsinki.localize(datetime(2011, 10, 3, 18, 34)),
            recurrence='RRULE:FREQ=YEARLY\r\nEXDATE:20131003T154000Z,20151003T154000Z'))

        # And now query for it with no end.
        # If the index does not handle this case specially, we'd
        # generate recurrences until we ran out fo memory.
        res = index._apply_index({
            'event': {
                'start': helsinki.localize(datetime(2011, 10, 3)),
            }
        })
        self.assertEqual(len(res[0]), 1)
        self.assertTrue(1 in res[0])

        # And we also need to test for having events that do end together
        # with infinitely recurring events as well.
        index.index_object(2, TestOb(
            name='a',
            start=helsinki.localize(datetime(2011, 10, 3, 15, 40)),
            end=helsinki.localize(datetime(2011, 10, 3, 18, 34)),
            recurrence='RRULE:FREQ=DAILY;INTERVAL=10;COUNT=5'))

        res = index._apply_index({
            'event': {
                'start': helsinki.localize(datetime(2011, 10, 3)),
            }
        })
        self.assertEqual(len(res[0]), 2)
        self.assertTrue(1 in res[0])
        self.assertTrue(2 in res[0])

        # Now search after the ending event ends, and we'll only get the
        # neverending recurrence back.

        res = index._apply_index({
            'event': {
                'start': helsinki.localize(datetime(2012, 10, 3)),
            }
        })
        self.assertEqual(len(res[0]), 1)
        self.assertTrue(1 in res[0])

