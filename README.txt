Introduction
============

plone.app.eventindex is an attempt to make a sane index for finding events
that support recurring events and is reasonably fast. Most importantly
existing solutions will calculate the recurrence-times at index-time. This
means events need to be reindexed after a time, and it also means you can't
support events that repeat more often than once a day, because it becomes
impractical to search for events otherwise.

This index will instead calculate the recurrence when searching. This has
the potential to cause problems if you create objects that will recur once
every second and have a very long end-date. In these cases we'll just include
the first 10000 recurrences. But otherwise the implementation is simpler, 
cleaner and more flexible.

Todo
----

* Tests with timezones
* More tests with recurrence
* Functional tests with a whole Plone-site
* Decide how to handle timezone-naive dates (and test that)

Credits
-------

plone.app.eventindex is created by Lennart Regebro, regebro@gmail.com

Thanks to Nuxeo, http://www.nuxeo.com/

plone.app.eventindex is informed and inspired by Nuxeo's CalZope calendaring
product, also authored by Lennart Regebro. Although this is a new product with
newly authored code, plone.app.eventindex would not have been possible without
Nuxeo.
