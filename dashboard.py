#!/usr/bin/env python

"""Basic dashboard datasets, similar to JIRA dashboard

"""
import settings

import json

import pymongo


class Dashboard(object):

    def __init__(self, host=settings.HOST, database=settings.DATABASE):

        self.client = pymongo.MongoClient(host)
        self.db = self.client[database]
        self.issues = self.db.issues

        self.dashboard = {}


class BaseDashboard(Dashboard):

    def calculate_summary(self):

        segment_base = {}

        key_str = "fields.status.name"
        query_str = '{"fields.status.name": "%s"}'
        record_str = '{"Status": "%s", "Issues": "%d", "Percentage": "%.f"}'

        summary = self.__calculate_segment(segment_base, key_str, query_str,
                                           record_str)

        self.dashboard.update({"summary": summary})

    def calculate_unresolved_by_priority(self):

        segment_base = {"fields.status.name": "Open"}

        key_str = "fields.priority.name"
        query_str = '''{"fields.status.name": "Open",
        "fields.priority.name": "%s"}'''
        record_str = '{"Priority": "%s", "Issues": "%d", "Percentage": "%.f"}'

        summary = self.__calculate_segment(segment_base, key_str, query_str,
                                           record_str)

        self.dashboard.update({
            "Unresolved: By Priority": summary
        })

    def calculate_unresolved_by_assignee(self):

        segment_base = {"fields.status.name": "Open"}

        key_str = "fields.assignee.displayName"
        query_str = '''{"fields.status.name": "Open",
            "fields.assignee.displayName": "%s"}'''
        record_str = '{"Assignee": "%s", "Issues": "%d", "Percentage": "%.f"}'

        summary = self.__calculate_segment(segment_base, key_str, query_str,
                                           record_str)

        self.dashboard.update({
            "Unresolved: By Assignee": summary
        })

    def calculate_unresolved_by_component(self):

        segment_base = {"fields.status.name": "Open"}

        key_str = "fields.components.name"
        query_str = '''{"fields.status.name": "Open",
            "fields.components.name": "%s"}'''
        record_str = '{"Component": "%s", "Issues": "%d", "Percentage": "%.f"}'

        summary = self.__calculate_segment(segment_base, key_str, query_str,
                                           record_str)

        self.dashboard.update({
            "Unresolved: By Component": summary
        })

    def calculate_unresolved_by_issue_type(self):

        segment_base = {"fields.status.name": "Open"}

        key_str = "fields.issuetype.name"
        query_str = '''{"fields.status.name": "Open",
            "fields.issuetype.name": "%s"}'''
        record_str = '{"Issue Type": "%s", "Issues": "%d", "Percentage": "%.f"}'

        summary = self.__calculate_segment(segment_base, key_str, query_str,
                                           record_str)

        self.dashboard.update({
            "Unresolved: By Issue Type": summary
        })

    def calculate_unresolved_by_version(self):

        segment_base = {"fields.status.name": "Open"}

        key_str = "fields.versions.name"
        query_str = '''{"fields.status.name": "Open",
            "fields.versions.name": "%s"}'''
        record_str = '{"Version": "%s", "Issues": "%d", "Percentage": "%.f"}'

        summary = self.__calculate_segment(segment_base, key_str, query_str,
                                           record_str)

        self.dashboard.update({
            "Unresolved: By Version": summary
        })

    def __calculate_segment(self, segment_base, key_field, query_str,
                            record_str):

        base_issue_count = self.issues.find(segment_base).count()

        summary = []

        for key in self.issues.distinct(key_field):
            query_json = json.loads(query_str % key)
            value = self.issues.find(query_json).count()
            if value:
                percentage = float(value) / float(base_issue_count) * 100
            else:
                percentage = 0.0

            if value == 0:
                continue

            record = json.loads(record_str % (key, value, percentage))
            summary.append(record)

        return summary
