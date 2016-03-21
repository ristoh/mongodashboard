#!/usr/bin/env python

"""Issue Drilldown Dashboard

More detailed analysis on issue creators, sources and resolution times.
"""

from dashboard import Dashboard

import json
import logging

from flanker.addresslib import address
import pymongo


class IssueDashboard(Dashboard):

    def __init__(self):

        super(IssueDashboard, self).__init__()
        self.reporter_domains = self.db.reporter_domains

    def get_reporter_domains(self):

        self.domains = set()
        for addr in self.db.issues.distinct("fields.reporter.emailAddress"):
            try:
                parsed_addr = address.EmailAddress(addr)
                self.domains.add(parsed_addr.hostname)
            except IndexError:
                logging.debug("Invalid Address", addr)
            except AssertionError:
                logging.debug("Invalid Address", addr)

    def count_domains_for_issues(self):

        for domain in self.domains:
            count = self.issues.find({"fields.reporter.emailAddress":
                              {"$regex": "@" + domain}}).count()
            reporter_domain = {
                "hostname": domain,
                "issues": count
            }
            self.db.reporter_domains.insert(reporter_domain)

    def update_open_and_close_rates(self):

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
                closed_issue_percentage = 'NaN'

            self.reporter_domains.update({"hostname": domain['hostname']},
                                         { "$set":
                                            {"open_issues": open_issues,
                                            "open_issue_percentage": open_issue_percentage,
                                            "closed_issues": closed_issues,
                                            "closed_issue_percentage": closed_issue_percentage
                                            }
                                          }
                                         )
