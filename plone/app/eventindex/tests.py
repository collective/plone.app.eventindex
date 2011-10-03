import unittest
from datetime import datetime
from DateTime import DateTime

from plone.app.eventindex import EventIndex

class TestOb(object):

    def __init__(self, name, start, end, recurrence):
        self.name  = name
        self.start = start
        self.end  = end
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
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EventIndexTests))
    return suite
