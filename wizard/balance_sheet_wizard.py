import time
from ast import literal_eval

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import date_utils

class BalanceSheetWizard(models.TransientModel):
    _name = "balance.sheet.wizard"
    _description = "Balance Sheet Wizard"
    _inherit = "abstract.wizard"

    date_from = fields.Date(required=True, )
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    posted = fields.Boolean(required=True, default=False)

    def _print_report(self, report_type):
        self.ensure_one()
        data = self._prepare_report_subsidiary_ledger()
        report_name = "account_cn.balance_sheet"
        return (
            self.env['ir.actions.report'].search(
                [("report_name", "=", report_name), ("report_type", "=", report_type)],
                limit=1,
            ).report_action(self, data=data, config=False)
        )

    def _prepare_report_subsidiary_ledger(self):
        self.ensure_one()
        return {
            "wizard_id": self.id,
            "company_id": self.company_id.id,
            "company_name": self.company_id.name,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "posted": self.posted,
        }

    def _export(self, report_type):
        return self._print_report(report_type)

