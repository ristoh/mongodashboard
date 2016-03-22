#!/usr/bin/env python
"""Import Jira Issues into MongoDB Dashboard Application

"""

from dashboard import BaseDashboard
import settings

import json


class JiraIssueImporter(BaseDashboard):

    def __init__(self, raw_issues=[]):

        super(JiraIssueImporter, self).__init__()
        self.raw_issues = raw_issues

    def load_issues_json(self, filename=settings.INPUT_FILE):

        if self.raw_issues != []:
            raise Exception("raw input already exists")

        with open(filename, 'r') as fp:
            self.raw_issues = json.load(fp)

    def import_to_mongo(self):

        self.issues.insert_many(self.raw_issues)

    def normalize_issues(self):

        self.normalized_issues = self.db.normalized_issues

        for issue_raw in self.issues.find({}, {
            "fields.status.statusCategory.name": 1,
            "fields.status.description": 1,
            "fields.status.name": 1,
            "fields.creator.active": 1,
            "fields.creators.name": 1,
            "fields.watches.watchCount": 1,
            "fields.assignee.active": 1,
            "fields.assignee.displayName": 1,
            "fields.assignee.name": 1,
            "fields.lastViewed": 1,
            "fields.issueslinks": 1,
            "fields.votes.votes": 1,
            "fields.fixVersions": 1,
            "fields.priority.name": 1,
            "fields.updated": 1,
            "fields.subtasks": 1,
            "fields.description": 1,
            "fields.reporter.active": 1,
            "fields.reporter.name": 1,
            "fields.versions": 1,
            "fields.components": 1,
            "fields.created": 1,
            "fields.resolutiondate": 1,
            "fields.summary": 1,
            "fields.project.key": 1,
            "fields.issuetype.description": 1,
            "fields.issuetype.name": 1,
            "fields.resolution.description": 1,
            "fields.resolution.name": 1,
            "id": 1}):
                self.normalized_issues.insert(issue_raw)
