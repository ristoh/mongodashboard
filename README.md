MongoDashboard
==============


Simple python program to present data for MongoDB Issue Dashboard


Import Data to MongoDB
----------------------

```
>>> from mongodashboard.importer import JiraIssueImporter
>>> importer = JiraIssueImporter(exporter.raw_issues)
>>> importer.import_to_mongo()
```

Calculate Basic Dashboard
-------------------------

```
>>> from mongodashboard.dashboard import Dashboard
>>> d = Dashboard()
>>> d.calculate_dashboard()
```

Calculate Further Details on Issues
-----------------------------------

```
>>> from mongodashboard.issuedashboard import IssueDashboard
>>> idash = IssueDashboard()
>>> idash.calculate_issue_analytics_collections()
```




