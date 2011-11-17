import unittest2 as unittest


class TestManageAddEventIndexForm(unittest.TestCase):

    def test_manage_addEventIndexForm(self):
        from plone.app.eventindex import manage_addEventIndexForm
        from App.special_dtml import DTMLFile
        self.assertTrue(isinstance(manage_addEventIndexForm, DTMLFile))
        self.assertEqual(manage_addEventIndexForm.name(), 'addEventIndex')
