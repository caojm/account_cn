from odoo import api, fields, models


class AccountCnAccountingBook(models.Model):
    _name = "account.cn.accounting.book"
    _description = "Accounting Book"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    code = fields.Char()
    name = fields.Char()
    currency_id = fields.Many2one("res.currency")
