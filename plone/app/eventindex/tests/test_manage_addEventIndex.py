import mock
import unittest2 as unittest


class TestManageAddEventIndex(unittest.TestCase):

    def test_manage_addEventIndex(self):
        self = mock.Mock()
        id = mock.Mock()
        extra = mock.Mock()
        REQUEST = mock.Mock()
        RESPONSE = mock.Mock()
        URL3 = mock.Mock()
        from plone.app.eventindex import manage_addEventIndex
        manage_addEventIndex(
            self,
            id,
            extra=extra,
            REQUEST=REQUEST,
            RESPONSE=RESPONSE,
            URL3=URL3,
        )
        self.manage_addIndex.assert_called_with(
            id,
            'EventIndex',
            extra=extra,
            REQUEST=REQUEST,
            RESPONSE=RESPONSE,
            URL1=URL3
        )
