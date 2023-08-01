from odoo.tools import frozendict, formatLang, format_date, float_compare, Query
from odoo import api, fields, models


class AccountCnVoucherLine(models.Model):
    _name = "account.cn.voucher.line"
    _inherit = "analytic.mixin"
    _description = "Voucher Entry"

    voucher_id = fields.Many2one(
        "account.cn.voucher",
        ondelete="cascade",
    )
    company_id = fields.Many2one(
        related="voucher_id.company_id",
        store=True,
    )
    accounting_book_id = fields.Many2one(
        related="voucher_id.accounting_book_id",
        store=True,
    )
    book_currency_id = fields.Many2one(
        related="accounting_book_id.currency_id",
    )
    date = fields.Date(
        related="voucher_id.date",
        store=True,
    )
    voucher_word = fields.Many2one(
        related="voucher_id.word_id",
        store=True,
    )
    voucher_number = fields.Integer(
        related="voucher_id.number",
        store=True,
    )
    voucher_state = fields.Selection(
        related="voucher_id.state",
    )
    include_cash_flow = fields.Boolean(
        related="voucher_id.include_cash_flow",
        store=True,
    )

    summary = fields.Char(
        compute="_compute_summary",
        store=True,
        readonly=False,
    )
    account_id = fields.Many2one(
        "account.account",
        required=True,
        check_company=True,
    )
    account_code = fields.Char(
        related="account_id.code",
        store=True,
    )
    account_code_length = fields.Integer(
        compute="_compute_account_code_length",
    )
    account_tag_ids = fields.Many2many(
        relation="account_cn_voucher_line_and_account_account_tag_rel",
        column1="voucher_line",
        column2="account_tag",
        string="Account tag",
        related="account_id.tag_ids",
        store=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        compute="_compute_partner_id",
        store=True,
        readonly=False,
        check_company=True,
    )
    currency_id = fields.Many2one("res.currency")
    amount_currency = fields.Monetary()
    debit = fields.Monetary(
        compute="_compute_debit_credit",
        inverse="_inverse_debit",
        store=True,
        readonly=False,
        # precompute=True,
        currency_field="book_currency_id",
    )
    credit = fields.Monetary(
        compute="_compute_debit_credit",
        inverse="_inverse_credit",
        store=True,
        readonly=False,
        # precompute=True,
        currency_field="book_currency_id",
    )
    sequence = fields.Integer(
        default=10,
    )
    tag_ids = fields.Many2many(
        "account.cn.voucher.tag",
    )

    @api.depends("voucher_id")
    def _compute_debit_credit(self):
        for line in self:
            balance = sum((line.voucher_id.line_ids - line).mapped("debit")) - sum(
                (line.voucher_id.line_ids - line).mapped("credit")
            )
            line.debit = -balance if balance < 0.0 else 0.0
            line.credit = balance if balance > 0.0 else 0.0

    @api.onchange("debit")
    def _inverse_debit(self):
        for line in self:
            if line.debit:
                line.credit = 0.0

    @api.onchange("credit")
    def _inverse_credit(self):
        for line in self:
            if line.credit:
                line.debit = 0.0

    @api.depends("voucher_id")
    def _compute_summary(self):
        for line in self:
            if not line.summary:
                old_lines = line.voucher_id.line_ids - line
                if old_lines:
                    line.summary = old_lines[-1].summary

    @api.depends("voucher_id")
    def _compute_partner_id(self):
        for line in self:
            if not line.partner_id:
                old_lines = line.voucher_id.line_ids - line
                if old_lines:
                    line.partner_id = old_lines[-1].partner_id

    @api.depends("account_id.code")
    def _compute_account_code_length(self):
        for line in self:
            line.account_code_length = len(line.account_id.code)
