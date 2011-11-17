import mock
import unittest2 as unittest


class TestInitialize(unittest.TestCase):

    @mock.patch('plone.app.eventindex.manage_addEventIndex')
    @mock.patch('plone.app.eventindex.manage_addEventIndexForm')
    @mock.patch('plone.app.eventindex.EventIndex')
    def test_initialize(self, EventIndex, manage_addEventIndexForm, manage_addEventIndex):
        from plone.app.eventindex import initialize
        context = mock.Mock()
        initialize(context)
        context.registerClass.assert_called_with(
            EventIndex,
            permission='Add Event Index',
            constructors=(
                manage_addEventIndexForm,
                manage_addEventIndex
            ),
            icon='www/index.gif',
            visibility=None,
        )
