import time
from ast import literal_eval

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import date_utils


class SubsidiaryLedgerWizard(models.TransientModel):
    _name = "subsidiary.ledger.wizard"
    _description = "Subsidiary Ledger Wizard"
    _inherit = "report.abstract.wizard"

    account_id = fields.Many2one("account.account")
    date_from = fields.Date(
        required=True,
    )
    date_to = fields.Date(required=True, default=fields.Date.context_today)

    def _print_report(self, report_type):
        self.ensure_one()
        data = self._prepare_report_subsidiary_ledger()
        report_name = "account_cn.subsidiary_ledger"
        return (
            self.env["ir.actions.report"]
            .search(
                [("report_name", "=", report_name), ("report_type", "=", report_type)],
                limit=1,
            )
            .report_action(self, data=data, config=False)
        )

    def _prepare_report_subsidiary_ledger(self):
        self.ensure_one()
        return {
            "wizard_id": self.id,
            "company_id": self.company_id.id,
            "account_id": self.account_id.id,
            "account_name": self.account_id.display_name,
            "date_from": self.date_from,
            "date_to": self.date_to,
        }

    def _export(self, report_type):
        return self._print_report(report_type)
