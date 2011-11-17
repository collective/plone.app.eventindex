import mock
import unittest2 as unittest


class MockRec(object):
    pass


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
    def test__init__attributes_without_extra(self, clear):
        instance = self.createInstance()
        self.assertEqual(instance._id, 'id')
        self.assertEqual(instance.start_attr, 'start')
        self.assertEqual(instance.end_attr, 'end')
        self.assertEqual(instance.recurrence_attr, 'recurrence')
        self.assertTrue(clear.called)

    @mock.patch('plone.app.eventindex.EventIndex.clear')
    def test__init__attributes_with_extra(self, clear):
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

    @mock.patch('plone.app.eventindex.IOBTree')
    @mock.patch('plone.app.eventindex.OOBTree')
    @mock.patch('plone.app.eventindex.Length')
    def test_clear(self, Length, OOBTree, IOBTree):
        instance = self.createInstance()
        Length.reset_mock()
        OOBTree.reset_mock()
        IOBTree.reset_mock()
        Length.return_value = 'length'
        OOBTree.return_value = 'oobtree'
        IOBTree.return_value = 'iobtree'
        instance.clear()
        self.assertEqual(Length.call_count, 1)
        self.assertEqual(OOBTree.call_count, 2)
        self.assertEqual(IOBTree.call_count, 4)
        self.assertEqual(instance._length, 'length')
        self.assertEqual(instance._end2uid, 'oobtree')
        self.assertEqual(instance._start2uid, 'oobtree')
        self.assertEqual(instance._uid2end, 'iobtree')
        self.assertEqual(instance._uid2duration, 'iobtree')
        self.assertEqual(instance._uid2start, 'iobtree')
        self.assertEqual(instance._uid2recurrence, 'iobtree')

    def test_getId(self):
        instance = self.createInstance()
        self.assertEqual(instance.getId(), 'id')

    def test_getEntryForObject(self):
        ## Should we implement something rather than raise NotImplementedError?
        instance = self.createInstance()
        self.assertRaises(
            NotImplementedError,
            lambda: instance.getEntryForObject(mock.Mock())
        )

    def test_getIndexSourceNames(self):
        instance = self.createInstance()
        instance.start_attr = 'start'
        instance.end_attr = 'end'
        instance.recurrence_attr = 'recurrence'
        self.assertEqual(
            instance.getIndexSourceNames(),
            ('start', 'end', 'recurrence')
        )

    def test__getattr(self):
        instance = self.createInstance()
        ## Test with attribute
        obj = mock.Mock()
        obj.attr = 'ATTR'
        self.assertEqual(instance._getattr('attr', obj), 'ATTR')
        ## Test method but not DateTime
        obj.method = mock.Mock(return_value='METHOD')
        self.assertEqual(instance._getattr('method', obj), 'METHOD')
        ## Test method which is DateTime
        from DateTime import DateTime
        dt = mock.Mock(spec=DateTime)
        date_time = mock.Mock(return_value=dt)
        date_time().utcdatetime.return_value = 'datetime'
        obj.method = date_time
        self.assertEqual(instance._getattr('method', obj), 'datetime')

    # @mock.patch('plone.app.eventindex.rrule')
    @mock.patch('plone.app.eventindex.IITreeSet')
    def test_index_object(self, IITreeSet):
        instance = self.createInstance()
        ## Test when start, end and recurrence is None
        documentId = 2
        obj = mock.MagicMock()
        obj.start = None
        obj.end = None
        obj.recurrence = None
        self.assertFalse(instance.index_object(documentId, obj))
        ## Test when start is not None, but end and recurrence is None
        obj.start = mock.MagicMock()
        obj.start().__sub__.return_value = 3
        obj.start().utctimetuple.return_value = 'Start Value'
        ## row is None
        self.assertTrue(instance.index_object(documentId, obj))
        self.assertEqual(len(instance._uid2start), 1)
        self.assertEqual(instance._uid2start[documentId], 'Start Value')
        self.assertEqual(len(instance._uid2recurrence), 1)
        self.assertFalse(instance._uid2recurrence[documentId])
        self.assertEqual(len(instance._uid2end), 1)
        self.assertEqual(instance._uid2end[documentId], 'Start Value')
        self.assertEqual(len(instance._uid2duration), 1)
        self.assertEqual(instance._uid2duration[documentId], 3)
        ## Test start and end are not None and recurrence is None
        obj.end = mock.Mock()
        obj.end().utctimetuple.return_value = 'End Value'
        self.assertTrue(instance.index_object(documentId, obj))
        self.assertEqual(instance._uid2end[documentId], 'End Value')
        ## start_row is not None
        instance._start2uid = mock.Mock()
        row = mock.Mock()
        instance._start2uid = {'Start Value': row}
        self.assertTrue(instance.index_object(documentId, obj))
        self.assertEqual(row.insert.call_count, 1)
        ## end_row is not None
        instance._end2uid = mock.Mock()
        instance._end2uid = {'End Value': row}
        row.insert.reset_mock()
        self.assertTrue(instance.index_object(documentId, obj))
        self.assertEqual(row.insert.call_count, 2)
        ## recurrence is not None
        obj.recurrence = mock.Mock()
        self.assertTrue(instance.index_object(documentId, obj))

    @mock.patch('plone.app.eventindex.rrule')
    @mock.patch('plone.app.eventindex.IITreeSet')
    def test_index_object_recurrence_basestring(self, IITreeSet, rrule):
        instance = self.createInstance()
        documentId = 2
        obj = mock.MagicMock()
        obj.start = mock.Mock()
        obj.start().utctimetuple.return_value = 'Start Value'
        obj.end = mock.MagicMock()
        obj.end().utctimetuple.return_value = 'End Value'
        obj.end().__sub__.return_value = 3
        obj.recurrence.return_value = mock.Mock(spec=basestring)
        dur = mock.MagicMock()
        duration = mock.Mock()
        dur.__add__.return_value = duration
        rule = mock.Mock()
        rrule.rrulestr.return_value = rule
        rrule.rrulestr()._iter.return_value = [dur]
        duration.utctimetuple.return_value = 'last'
        self.assertTrue(instance.index_object(documentId, obj))
        self.assertEqual(len(instance._uid2start), 1)
        self.assertEqual(instance._uid2start[documentId], 'Start Value')
        self.assertEqual(len(instance._uid2recurrence), 1)
        self.assertEqual(instance._uid2recurrence[documentId], rule)
        self.assertEqual(len(instance._uid2end), 1)
        self.assertEqual(instance._uid2end[documentId], 'last')
        self.assertEqual(len(instance._uid2duration), 1)
        self.assertEqual(instance._uid2duration[documentId], 3)
        rule.count = None
        self.assertTrue(instance.index_object(documentId, obj))
        self.assertEqual(instance._uid2end[documentId], 'last')
        rule.until = None
        self.assertTrue(instance.index_object(documentId, obj))
        self.assertFalse(instance._uid2end[documentId])

    @mock.patch('plone.app.eventindex.IITreeSet')
    def test_index_object_recurrence_rrulebase(self, IITreeSet):
        instance = self.createInstance()
        documentId = 2
        obj = mock.MagicMock()
        obj.start = mock.Mock()
        obj.start().utctimetuple.return_value = 'Start Value'
        obj.end = mock.MagicMock()
        obj.end().utctimetuple.return_value = 'End Value'
        obj.end().__sub__.return_value = 3
        from dateutil.rrule import rrulebase
        rule = mock.Mock(spec=rrulebase)
        obj.recurrence.return_value = rule
        rule.count = rule.until = None
        self.assertTrue(instance.index_object(documentId, obj))
        self.assertEqual(len(instance._uid2start), 1)
        self.assertEqual(instance._uid2start[documentId], 'Start Value')
        self.assertEqual(len(instance._uid2recurrence), 1)
        self.assertEqual(instance._uid2recurrence[documentId], rule)
        self.assertEqual(len(instance._uid2end), 1)
        self.assertFalse(instance._uid2end[documentId])
        self.assertEqual(len(instance._uid2duration), 1)
        self.assertEqual(instance._uid2duration[documentId], 3)

    def test_remove_id(self):
        instance = self.createInstance()
        documentId = 2
        point = 'start'
        instance._uid2start = mock.Mock()
        instance.remove_id(documentId, point)
        self.assertTrue(instance._uid2start.pop.called)
        instance._uid2start.pop.return_value = 3
        instance._start2uid = mock.Mock()
        instance._start2uid.get.return_value = [1]
        instance.remove_id(documentId, point)
        self.assertTrue(instance._start2uid.get.called)
        self.assertEqual(instance._start2uid.get(), [1])
        instance._start2uid.get.return_value = [1, 2, 3, 4]
        instance.remove_id(documentId, point)
        self.assertEqual(instance._start2uid.get(), [1, 3, 4])
        documentId = 3
        instance.remove_id(documentId, point)
        self.assertEqual(instance._start2uid.get(), [1, 4])

    def test_unindex_object(self):
        instance = self.createInstance()
        documentId = mock.Mock()
        instance.remove_id = mock.Mock()
        instance._uid2duration = mock.Mock()
        instance._uid2recurrence = mock.Mock()
        instance.unindex_object(documentId)
        self.assertEqual(instance.remove_id.call_count, 2)
        self.assertTrue(instance._uid2duration.pop.called)
        self.assertTrue(instance._uid2recurrence.pop.called)

    def test_get_position_without_key(self):
        instance = self.createInstance()
        instance._id = 2
        position = 'start'
        request = {}
        self.assertRaises(KeyError, lambda: instance.get_position(request, position))

    def test_get_position_with_key(self):
        instance = self.createInstance()
        instance._id = 2
        position = 'start'
        pos = mock.Mock()
        posi = mock.Mock()
        pos.get.return_value = posi
        request = {2: pos}
        self.assertEqual(
            instance.get_position(request, position),
            posi
        )

    def test_get_positin_with_key_and_datetime_instance(self):
        instance = self.createInstance()
        instance._id = 2
        position = 'start'
        from DateTime import DateTime
        pos = mock.Mock()
        posi = mock.Mock(spec=DateTime)
        pos.get.return_value = posi
        pos.get().utcdatetime.return_value = 'utcdatetime'
        request = {2: pos}
        self.assertEqual(
            instance.get_position(request, position),
            'utcdatetime'
        )

    @mock.patch('plone.app.eventindex.IITreeSet')
    def test_aaa_results_empty(self, IITreeSet):
        instance = self.createInstance()
        IITreeSet.return_value = 'iitreeset'
        result = []
        start = mock.Mock()
        end = mock.Mock()
        used_fields = mock.Mock()
        self.assertEqual(
            instance.aaa(result, start, end, used_fields),
            ('iitreeset', used_fields)
        )

    @mock.patch('plone.app.eventindex.IITreeSet')
    def test_aaa_reuccurence_none(self, IITreeSet):
        instance = self.createInstance()
        result = [1, 2, 3, 4]
        start = None
        end = None
        used_fields = mock.Mock()
        self.assertEqual(
            instance.aaa(result, start, end, used_fields),
            (IITreeSet(), used_fields)
        )
        self.assertEqual(IITreeSet().add.call_count, 4)

    @mock.patch('plone.app.eventindex.IITreeSet')
    def test_aaa_reuccurence_not_none(self, IITreeSet):
        instance = self.createInstance()
        result = [1, 2, 3, 4]
        start = None
        end = None
        used_field = mock.Mock()
        used_fields = (used_field,)
        instance._uid2recurrence = mock.Mock()
        instance._uid2recurrence.get.return_value = mock.Mock()
        occurence = mock.Mock()
        occurence.utctimetuple.return_value = (2006, 6, 14, 13, 0, 0)
        instance._uid2recurrence.get()._iter.return_value = [occurence]
        self.assertEqual(
            instance.aaa(result, start, end, used_fields),
            (
                IITreeSet(),
                (
                    used_field,
                    'recurrence',
                    'recurrence',
                    'recurrence',
                    'recurrence'
                )
            )
        )
        self.assertEqual(IITreeSet().add.call_count, 4)

    @mock.patch('plone.app.eventindex.IITreeSet')
    def test_aaa_reuccurence_not_iterable(self, IITreeSet):
        instance = self.createInstance()
        result = [1, 2, 3, 4]
        start = None
        end = None
        used_field = mock.Mock()
        used_fields = (used_field,)
        instance._uid2recurrence = mock.Mock()
        instance._uid2recurrence.get.return_value = mock.Mock()
        instance._uid2recurrence.get()._iter.return_value = []
        self.assertEqual(
            instance.aaa(result, start, end, used_fields),
            (
                IITreeSet(),
                (
                    used_field,
                    'recurrence',
                    'recurrence',
                    'recurrence',
                    'recurrence'
                )
            )
        )
        self.assertEqual(IITreeSet().add.call_count, 0)

    @mock.patch('plone.app.eventindex.IITreeSet')
    def test_aaa_reuccurence_event_start_bigger(self, IITreeSet):
        instance = self.createInstance()
        result = [1, 2, 3, 4]
        start = mock.Mock()
        end = None
        used_field = mock.Mock()
        used_fields = (used_field,)
        dt = (2006, 6, 15, 13, 0, 0)
        instance._uid2start = dict(
            [(key, dt) for key in result]
        )
        occurence = mock.Mock()
        occurence.utctimetuple.return_value = (2006, 6, 14, 13, 0, 0)
        instance._uid2recurrence = mock.Mock()
        instance._uid2recurrence.get.return_value = mock.Mock()
        instance._uid2recurrence.get()._iter.return_value = [occurence]
        self.assertEqual(
            instance.aaa(result, start, end, used_fields),
            (
                IITreeSet(),
                (
                    used_field,
                    'recurrence',
                    'recurrence',
                    'recurrence',
                    'recurrence'
                )
            )
        )
        self.assertEqual(IITreeSet().add.call_count, 0)

    @mock.patch('plone.app.eventindex.IITreeSet')
    def test_aaa_reuccurence_event_start_smaller(self, IITreeSet):
        instance = self.createInstance()
        result = [1, 2, 3, 4]
        start = mock.Mock()
        end = mock.Mock()
        used_field = mock.Mock()
        used_fields = (used_field,)
        dt = (2006, 6, 11, 13, 0, 0)
        instance._uid2start = dict(
            [(key, dt) for key in result]
        )
        from datetime import datetime
        dur = datetime(2006, 6, 14) - datetime(2006, 6, 13)
        instance._uid2duration = dict(
            [(key, dur) for key in result]
        )
        occurence = mock.Mock()
        occurence.utctimetuple.return_value = (2006, 6, 14, 13, 0, 0)
        instance._uid2recurrence = mock.Mock()
        instance._uid2recurrence.get.return_value = mock.Mock()
        instance._uid2recurrence.get()._iter.return_value = [occurence]
        self.assertEqual(
            instance.aaa(result, start, end, used_fields),
            (
                IITreeSet(),
                (
                    used_field,
                    'recurrence',
                    'recurrence',
                    'recurrence',
                    'recurrence'
                )
            )
        )
        self.assertEqual(IITreeSet().add.call_count, 0)

    @mock.patch('plone.app.eventindex.IITreeSet')
    def test__apply_index__no_id(self, IITreeSet):
        instance = self.createInstance()
        request = mock.Mock()
        request.has_key.return_value = None
        IITreeSet.return_value = 'iitreeset'
        self.assertEqual(
            instance._apply_index(request),
            ('iitreeset', ())
        )

    @mock.patch('plone.app.eventindex.IITreeSet')
    def test__apply_index__with_id_without_maxkey(self, IITreeSet):
        instance = self.createInstance()
        request = mock.Mock()
        instance.get_position = mock.Mock()
        instance._end2uid = mock.Mock()
        instance._end2uid.maxKey = mock.Mock(side_effect=ValueError)
        IITreeSet.return_value = 'iitreeset'
        self.assertEqual(
            instance._apply_index(request),
            ('iitreeset', ())
        )

    # @mock.patch('plone.app.eventindex.IITreeSet')
    # def test__apply_index__with_start_none(self, IITreeSet):
    #     instance = self.createInstance()
    #     request = mock.Mock()
    #     instance.get_position = mock.Mock(return_value=None)
    #     IITreeSet.return_value = [1, 2, 3]
    #     self.assertEqual(
    #         instance._apply_index(request),
    #         ('iitreeset', ())
    #     )

    # def test__apply_index__with_id(self):
    #     instance = self.createInstance()
    #     request = mock.Mock()
    #     instance._apply_index(request)
