import mock
import unittest2 as unittest


class TestUtcify(unittest.TestCase):

    def test_utificy(self):
        from plone.app.eventindex.tests.test_original import utcify
        from DateTime import DateTime
        dt = mock.Mock(spec=DateTime)
        utcify(dt)
        self.assertTrue(dt.utcdatetime.called)
        dt = mock.Mock()
        utcify(dt)
        self.assertTrue(dt.utctimetuple.called)
