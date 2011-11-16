import mock
import unittest2 as unittest


class TestEventIndex(unittest.TestCase):

    def createInstance(self, extra=None):
        from plone.app.eventindex import EventIndex
        return EventIndex('id', extra=extra)

    def test_class__inherits(self):
        from plone.app.eventindex import EventIndex
        from OFS.SimpleItem import SimpleItem
        self.assertTrue(issubclass(EventIndex, SimpleItem))

    def test_instance__provides(self):
        instance = self.createInstance()
        from Products.PluginIndexes.interfaces import IPluggableIndex
        self.assertTrue(IPluggableIndex.providedBy(instance))

    def test_instance__metatype(self):
        instance = self.createInstance()
        self.assertEqual(instance.meta_type, 'EventIndex')

    def test_instance__manage_options(self):
        instance = self.createInstance()
        self.assertEqual(
            instance.manage_options,
            (
                {
                    'label': 'Settings',
                    'action': 'manage_main'
                },
            )
        )

    def test_instance__manage(self):
        instance = self.createInstance()
        self.assertEqual(
            instance.manage,
            instance.manage_main
        )
        from App.special_dtml import DTMLFile
        self.assertTrue(isinstance(instance.manage, DTMLFile))
        self.assertEqual(instance.manage.name(), 'manage_main')

    @mock.patch('plone.app.eventindex.EventIndex.clear')
    def test_instance__init__attributes_without_extra(self, clear):
        instance = self.createInstance()
        self.assertEqual(instance._id, 'id')
        self.assertEqual(instance.start_attr, 'start')
        self.assertEqual(instance.end_attr, 'end')
        self.assertEqual(instance.recurrence_attr, 'recurrence')
        self.assertTrue(clear.called)

    @mock.patch('plone.app.eventindex.EventIndex.clear')
    def test_instance__init__attributes_with_extra(self, clear):
        extra = {
        }
        instance = self.createInstance(extra=extra)
        self.assertEqual(instance._id, 'id')
        self.assertEqual(instance.start_attr, 'start')
        self.assertEqual(instance.end_attr, 'end')
        self.assertEqual(instance.recurrence_attr, 'recurrence')
        self.assertTrue(clear.called)
        ## Set start_attr
        extra = {
            'start_attr': 'START',
        }
        self.assertRaises(KeyError, lambda: self.createInstance(extra=extra))
        ## Set start_attr and end_attr
        extra = {
            'start_attr': 'START',
            'end_attr': 'END',
        }
        self.assertRaises(KeyError, lambda: self.createInstance(extra=extra))
        ## Set start_attr, end_attr and recurrence_attr
        extra = {
            'start_attr': 'START',
            'end_attr': 'END',
            'recurrence_attr': 'RECURRENCE',
        }
        instance = self.createInstance(extra=extra)
        self.assertEqual(instance._id, 'id')
        self.assertEqual(instance.start_attr, 'START')
        self.assertEqual(instance.end_attr, 'END')
        self.assertEqual(instance.recurrence_attr, 'RECURRENCE')
        self.assertTrue(clear.called)
