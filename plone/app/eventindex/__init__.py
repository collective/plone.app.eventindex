from App.special_dtml import DTMLFile
from BTrees.IIBTree import IITreeSet
from BTrees.IIBTree import intersection
from BTrees.IIBTree import union
from BTrees.IIBTree import multiunion
from BTrees.IOBTree import IOBTree
from BTrees.Length import Length
from BTrees.OOBTree import OOBTree
from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from Products.PluginIndexes.interfaces import IPluggableIndex
from datetime import datetime
from dateutil import rrule
from zope.interface import implements

def is_open_ended(rule):
    if isinstance(rule, rrule.rruleset):
        rules = rule._rrule
    else:
        rules = [rule]
        
    for r in rules:
        if r._count is None and r._until is None:
            return True
        
    return False

def localize_datetime(dt, tz):
    if not isinstance(dt, datetime):
        return dt

    if tz is None and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    elif tz is not None and dt.tzinfo is None:
        return tz.localize(dt)
    else:
        return dt

def sync_timezone(rule, tz):
    if isinstance(rule, rrule.rruleset):
        if getattr(rule, '_exdate', None):
            rule._exdate = [localize_datetime(x, tz) for x in rule._exdate]
        if getattr(rule, '_rdate', None):
            rule._rdate = [localize_datetime(x, tz) for x in rule._rdate]
        for x in rule._rrule:
            sync_timezone(x, tz)
    else:
        if getattr(rule, '_until', None):
            rule._until = localize_datetime(rule._until, tz)
        if getattr(rule, '_dtstart', None):
            rule._dtstart = localize_datetime(rule._dtstart, tz)
        

class EventIndex(SimpleItem):

    implements(IPluggableIndex)

    meta_type = "EventIndex"

    manage_options= (
        {'label': 'Settings',
         'action': 'manage_main'},
    )

    manage = manage_main = DTMLFile('www/manageEventIndex', globals())
    manage_main._setName('manage_main')

    def __init__(self, id, extra=None, caller=None):
        self._id = id
        self.start_attr = extra and extra['start_attr'] or 'start'
        self.end_attr = extra and extra['end_attr'] or 'end'
        self.recurrence_attr = extra and extra['recurrence_attr'] or 'recurrence'
        self.clear()

    def clear(self):
        """Empty the index"""
        self._length = Length()
        self._end2uid = OOBTree()
        self._start2uid = OOBTree()
        self._uid2end = IOBTree()  # Contains the index used in _end2uid
        self._uid2duration = IOBTree()  # Contains the duration
        self._uid2start = IOBTree()
        self._uid2recurrence = IOBTree()

    def getId(self):
        """Return Id of index."""
        return self._id

    def getEntryForObject(self, documentId, default=''):
        """Get all information contained for 'documentId'."""
        uid2start = self._uid2start.get(documentId)
        if uid2start:
            return {
                'start': uid2start,
                'end': self._uid2end[documentId],
                'recurrence': self._uid2recurrence[documentId],
                'duration': self._uid2duration[documentId]
            }
        else:
            return default

    def getIndexSourceNames(self):
        """Get a sequence of attribute names that are indexed by the index.
        """
        return self.start_attr, self.end_attr, self.recurrence_attr

    def _getattr(self, name, obj):
        attr = getattr(obj, name, None)
        if callable(attr):
            attr = attr()

        if isinstance(attr, DateTime):
            attr = attr.utcdatetime()
        return attr

    def index_object(self, documentId, obj, threshold=None):
        """Index an object.

        - ``documentId`` is the integer ID of the document.

        - ``obj`` is the object to be indexed.

        - ``threshold`` is the number of words to process between committing
          subtransactions.  If None, subtransactions are disabled.

        For each name in ``getIndexSourceNames``, try to get the named
        attribute from ``obj``.

        - If the object does not have the attribute, do not add it to the
          index for that name.

        - If the attribute is a callable, call it to get the value.  If
          calling it raises an AttributeError, do not add it to the index.
          for that name.
        """

        ### 1. Get the values.
        start = self._getattr(self.start_attr, obj)
        end = self._getattr(self.end_attr, obj)
        if start is None:
            # Ignore calls if the obj does not have the start field.
            return False

        if end is None:
            # Singular event
            end = start

        recurrence = self._getattr(self.recurrence_attr, obj)
        if not recurrence:
            rule = None
        elif isinstance(recurrence, basestring):
            # XXX trap and log errors
            rule = rrule.rrulestr(recurrence, dtstart=start)
        elif isinstance(recurrence, rrule.rrulebase):
            rule = recurrence
        else:
            #XXX Log error
            rule = None

        # Strip out times from the recurrence:
        if rule is not None:
            sync_timezone(rule, start.tzinfo)
            
        ### 2. Make them into what should be indexed.
        # XXX Naive events are not comparable to timezoned events, so we convert
        # everything to utctimetuple(). This means naive events are assumed to
        # be GMT, but we can live with that at the moment.
        start_value = start.utctimetuple()
        end_value = end.utctimetuple()

        # The end value should be the end of the recurrence, if any:
        if rule is not None:
            if is_open_ended(rule):
                # This recurrence is open ended
                end_value = None
            else:
                duration = end - start
                allrecs = [x for x in rule._iter()]
                if allrecs:
                    last = allrecs[-1] + duration
                else:
                    # Real data may have invalud recurrence rules,
                    # which end before the start for example.
                    # Then we end up here.
                    last = end
                end_value = last.utctimetuple()

        ### 3. Store everything in the indexes:
        row = self._start2uid.get(start_value, None)
        if row is None:
            row = IITreeSet((documentId,))
            self._start2uid[start_value] = row
        else:
            row.insert(documentId)

        row = self._end2uid.get(end_value, None)
        if row is None:
            row = IITreeSet((documentId,))
            self._end2uid[end_value] = row
        else:
            row.insert(documentId)

        self._uid2start[documentId] = start_value
        self._uid2recurrence[documentId] = rule
        self._uid2end[documentId] = end_value
        self._uid2duration[documentId] = end - start

        return True

    def _remove_id(self, documentId, from_uid, to_uid):
        """Remove documentId based on point.
        Helper method for unindex_object method.

        :param documentId: Integer
        :type documentId: int

        :param from_uid:
        :type to_uid:

        :param to_uid:
        :type to_uid:
        """
        fuid = from_uid.pop(documentId, 'No ID found')
        row = to_uid.get(fuid)
        if row is not None:
            if documentId in row:
                row.remove(documentId)
            if len(row) == 0:
                to_uid.pop(fuid, 'Not Found')

    def unindex_object(self, documentId):
        """Remove the documentId from the index."""
        self._remove_id(documentId, self._uid2start, self._start2uid)
        self._remove_id(documentId, self._uid2end, self._end2uid)
        self._uid2duration.pop(documentId, 'No ID found')
        self._uid2recurrence.pop(documentId, 'No ID found')

    def _get_position(self, request, position):
        """Get position from certain ID.

        :param request: Request
        :type request: object

        :param position: start or end
        :type position: str
        """
        pos = request[self._id].get(position)
        if isinstance(pos, DateTime):
            pos = pos.utcdatetime()
        return pos

    def _finalize_index(self, result, start, end, used_fields):
        filtered_result = IITreeSet()
        # used_recurrence = False

        for documentId in result:
            recurrence = self._uid2recurrence.get(documentId)
            if recurrence is None:
                # This event isn't recurring, so it's a match:
                filtered_result.add(documentId)
                continue

            # used_recurrence = True
            match = False
            # This is a possible place where optimizations can be done if
            # necessary. For example, for periods where the start and end
            # date is the same, we can first check if the start time and
            # and time of the date falls inbetween the start and end times
            # of the period, so to avoid expansion. But most likely this
            # will have a very small impact on speed, so I skip this until
            # it actually becomes a problem.

            if start is not None:
                event_start = datetime(*self._uid2start[documentId][:6])
            else:
                event_start = None
            if end is not None:
                event_duration = self._uid2duration[documentId]
                event_end = event_start + event_duration
            else:
                event_end = None

            for occurrence in recurrence._iter():
                utc_occurrence = datetime(*occurrence.utctimetuple()[:6])
                if event_start is not None and utc_occurrence < event_start:
                    # XXX we should add a counter and break after 10000 occurrences.
                    continue
                if event_end is not None and utc_occurrence > event_end:
                    break

                # The start of this occurrence starts between the start and end date of
                # the query:
                match = True
                break

            if match:
                filtered_result.add(documentId)
            # if used_recurrence:
            used_fields += (self.recurrence_attr,)
        return filtered_result, used_fields

    def _apply_index(self, request, resultset=None):
        """Apply the index to query parameters given in 'request'.

        The argument should be a mapping object.

        If the request does not contain the needed parameters, then
        None is returned.

        If the request contains a parameter with the name of the
        column and this parameter is either a Record or a class
        instance then it is assumed that the parameters of this index
        are passed as attribute (Note: this is the recommended way to
        pass parameters since Zope 2.4)

        Otherwise two objects are returned.  The first object is a
        ResultSet containing the record numbers of the matching
        records.  The second object is a tuple containing the names of
        all data fields used.

        The resultset argument contains the resultset, as already calculated by
        ZCatalog's search method.
        """
        if not request.has_key(self._id):  # 'in' doesn't work with this object
            return IITreeSet(self._uid2end.keys()), ()

        start = self._get_position(request, 'start')
        end = self._get_position(request, 'end')

        used_fields = ()

        # We don't want the events who end before the start. In other
        # words we want to find those evens whose end >= the start query,
        # or None as None means they have infinite recurrence.
        try:
            maxkey = self._end2uid.maxKey()
        except ValueError:  # No events at all
            return IITreeSet(), used_fields

        if start is None or maxkey is None:
            # start is None, so we need to search right from the start; or
            # (amazingly) all events have infinite recurrence.
            # This means we must return *all* uids.
            start_uids = IITreeSet(self._uid2end.keys())
        else:
            used_fields += (self.start_attr,)
            #start_uids = IITreeSet()
            start = start.utctimetuple()
            try:
                minkey = self._end2uid.minKey(start)
                # Events that end on exactly the same same time as the
                # search period start should not be included:
                if minkey == start:
                    excludemin = True
                else:
                    excludemin = False

                start_uids = multiunion(self._end2uid.values(minkey, maxkey, excludemin=excludemin))
                    
            except ValueError:
                # No ending events
                start_uids = IITreeSet()
            
            # Include open ended events, if any
            if self._end2uid.has_key(None):
                start_uids = union(start_uids, self._end2uid[None])
            
        # XXX At this point an intersection with the resultset might be
        # beneficial. It would stop us from calculating the recurrence
        # of ids that won't be returned. It could be done after the
        # intersection with end_uids below as well, performance tests will tell.

        # We also do not want the events whose start come after the end query.
        # In other words, we find all events where start <= end.
        if end is not None:
            end = end.utctimetuple()
            try:
                minkey = self._start2uid.minKey()
                end_uids = multiunion(self._start2uid.values(minkey, end))
                used_fields += (self.end_attr,)

            except ValueError:
                # No events
                return IITreeSet(), used_fields

            result = intersection(start_uids, end_uids)
        else:
            # No end specified, take all:
            result = start_uids

        return self._finalize_index(result, start, end, used_fields)

    def numObjects(self):
        """Return the number of indexed objects."""
        return len(self._uid2start.keys())


manage_addEventIndexForm = DTMLFile('www/addEventIndex', globals())


def manage_addEventIndex(self, id, extra=None,
                REQUEST=None, RESPONSE=None, URL3=None):
    """Add an event index"""
    return self.manage_addIndex(id, 'EventIndex', extra=extra, \
             REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)


def initialize(context):
    context.registerClass(EventIndex,
                          permission='Add Event Index',
                          constructors=(manage_addEventIndexForm,
                                        manage_addEventIndex),
                          icon='www/index.gif',
                          visibility=None,
                         )
