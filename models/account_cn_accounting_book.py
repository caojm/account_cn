from odoo import api, fields, models


class AccountCnAccountingBook(models.Model):
    _name = "account.cn.accounting.book"
    _description = "Accounting Book"

    company_id = fields.Many2one(
        "res.company",
        # required=True,
        default=lambda self: self.env.company,
    )
    code = fields.Char(
        required=True,
    )
    name = fields.Char(
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
    )
    accounting_supervisor_id = fields.Many2one("res.users")
