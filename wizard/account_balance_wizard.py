import time
from ast import literal_eval

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import date_utils


class AccountBalanceWizard(models.TransientModel):
    _name = "account.balance.wizard"
    _description = "Account Balance Wizard"
    _inherit = "report.abstract.wizard"

    account_ids = fields.Many2many(
        "account.account",
    )
    max_account_code_length = fields.Integer(
        default=6,
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.user.accounting_book_id.currency_id,
    )
    date_from = fields.Date(
        required=True,
    )
    date_to = fields.Date(
        required=True,
        default=fields.Date.context_today,
    )
    posted_only = fields.Boolean(
        default=False,
    )
    exact_match = fields.Boolean(
        default=False,
    )
    distinguish_partner = fields.Boolean(
        default=False,
    )
    partner_ids = fields.Many2many(
        "res.partner",
    )
    voucher_type_ids = fields.Many2many(
        "account.cn.voucher.type",
    )
    tag_ids = fields.Many2many(
        "account.cn.voucher.tag",
    )
    accounting_book_ids = fields.Many2many(
        "account.cn.accounting.book",
        compute="_compute_accounting_book_ids",
        store=True,
        readonly=False,
        required=True,
        default=lambda self: self.env.user.accounting_book_id,
        domain="[('currency_id', '=', currency_id)]",
    )
    company_ids = fields.Many2many(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )

    def _print_report(self, report_type):
        self.ensure_one()
        data = self._prepare_report_subsidiary_ledger()
        report_name = "account_cn.account_balance"
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
            "company_ids": self.company_ids.ids,
            "accounting_book_ids": self.accounting_book_ids.ids,
            "currency_id": self.currency_id.id,
            "currency_name": self.currency_id.full_name,
            "account_ids": self.account_ids.ids,
            "max_account_code_length": self.max_account_code_length,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "posted_only": self.posted_only,
            "exact_match": self.exact_match,
            "distinguish_partner": self.distinguish_partner,
            "partner_ids": self.partner_ids.ids,
            "voucher_type_ids": self.voucher_type_ids.ids,
            "tag_ids": self.tag_ids.ids,
        }

    def _export(self, report_type):
        return self._print_report(report_type)

    @api.depends("currency_id")
    def _compute_accounting_book_ids(self):
        self.ensure_one()
        self.accounting_book_ids = self.accounting_book_ids.filtered(
            lambda r: r.currency_id == self.currency_id
        )
