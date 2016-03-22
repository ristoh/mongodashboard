#!/usr/bin/env python

"""Issue Drilldown Dashboard

More detailed analysis on issue creators, sources (reporting domains)
and resolution rates.
"""

from dashboard import BaseDashboard

import logging

from flanker.addresslib import address


class IssueDashboard(BaseDashboard):

    def __init__(self):

        super(IssueDashboard, self).__init__()
        self.reporter_domains = self.db.reporter_domains

    def calculate_issue_analytics_collections(self):

        self.get_reporter_domains()
        self.store_domains_for_issues()
        self.store_open_and_close_rates()
        self.store_component_issues()
        self.store_resolution_count()

    def get_reporter_domains(self):
        "a set of domains which have reported domains"

        self.domains = set()
        for addr in self.db.issues.distinct("fields.reporter.emailAddress"):
            try:
                parsed_addr = address.EmailAddress(addr)
                self.domains.add(parsed_addr.hostname)
            except IndexError:
                logging.debug("Invalid Address", addr)
            except AssertionError:
                logging.debug("Invalid Address", addr)

    def store_domains_for_issues(self):
        """update a db.reporter_domains collection

        store:
            hostname - reporting hostname
            issues - # of issues reported from that hostname
        """

        for domain in self.domains:
            count = self.issues.find({"fields.reporter.emailAddress": {"$regex": "@" + domain}}).count()
            reporter_domain = {
                "hostname": domain,
                "issues": count
            }
            self.db.reporter_domains.insert(reporter_domain)

    def store_open_and_close_rates(self):
        """update the db.reporter_domains with more issue stats

        update:
            open_issues - # of issues currently open
            open_issue_percentage - % of issues still open
            closed_issues - # of issues closed
            closed-issue_percentage - % of issues closed
        """

        for domain in self.reporter_domains.find():
            domain_name = "@" + domain['hostname']
            total_issues = domain['issues']
            open_issues = self.issues.find({"fields.status.name": "Open",
                                            "fields.reporter.emailAddress": {
                                                "$regex": domain_name}}).count()
            if float(total_issues) > 0.0:
                open_issue_percentage = float(open_issues) / float(total_issues) * 100
            else:
                open_issue_percentage = 'NaN'

            closed_issues = self.issues.find({"fields.status.name": "Closed",
                                            "fields.reporter.emailAddress": {
                                                "$regex": domain_name}}).count()

            if float(total_issues) > 0.0:
                closed_issue_percentage = float(closed_issues) / float(total_issues) * 100
            else:
                closed_issue_percentage = ''

            self.reporter_domains.update({"hostname": domain['hostname']},
                                         {"$set":
                                            {"open_issues": open_issues,
                                            "open_issue_percentage": open_issue_percentage,
                                            "closed_issues": closed_issues,
                                            "closed_issue_percentage": closed_issue_percentage
                                            }
                                          }
                                         )

    def store_resolution_count(self):
        """update db.reporter_domains with resolution name"""

        resolution_names = self.issues.distinct("fields.resolution.name")

        for domain in self.reporter_domains.find():
            domain_name = "@" + domain['hostname']
            update_record = {}
            for key in resolution_names:
                count = self.issues.find({"fields.reporter.emailAddress":
                                          {"$regex": domain_name},
                                          "fields.resolution.name": key}).count()
                update_record.update({
                    key: count
                })
            self.reporter_domains.update({"hostname": domain['hostname']},
                                         {"$set": update_record})

    def store_component_issues(self):
        """store db.component_issues collection"""

        component_issues = self.__get_issues_per_component()
        self.db.component_issues.insert_many(component_issues)

    def __get_issues_per_component(self):
        """calculate issues per component"""

        component_issues = []

        for component in self.issues.distinct("fields.components.name"):
            count = self.issues.find({"fields.components.name": component}).count()
            record = {
                "name": component,
                "issues": count
            }
            component_issues.append(record)

        return component_issues
