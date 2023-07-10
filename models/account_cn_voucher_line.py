from odoo.tools import frozendict, formatLang, format_date, float_compare, Query
from odoo import api, fields, models


class AccountCnVoucherLine(models.Model):
    _name = "account.cn.voucher.line"
    _inherit = "analytic.mixin"
    _description = "Account Voucher Entry"

    voucher_id = fields.Many2one("account.cn.voucher")
    company_id = fields.Many2one(
        related="voucher_id.company_id",
        store=True,
        readonly=True,
        precompute=True,
    )
    accounting_book_id = fields.Many2one(
        related="voucher_id.accounting_book_id",
        store=True,
        copy=True,
    )
    date = fields.Date(
        related="voucher_id.date",
        store=True,
        copy=False,
    )
    voucher_word = fields.Many2one(
        related="voucher_id.word_id",
        store=True,
    )
    voucher_number = fields.Char(
        related="voucher_id.number",
        store=True,
        copy=False,
    )
    voucher_state = fields.Selection(
        related="voucher_id.state",
        store=True,
        copy=False,
    )

    summary = fields.Char()
    account_id = fields.Many2one(
        "account.account",
        check_company=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        check_company=True,
    )
    debit = fields.Monetary()
    credit = fields.Monetary()
    currency_id = fields.Many2one("res.currency")
    sequence = fields.Integer(
        default=1,
    )
