from odoo import fields, models


class AccountCnVoucherType(models.Model):
    _name = "account.cn.voucher.type"
    _description = "Account Voucher Type"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    code = fields.Char()
    name = fields.Char()
