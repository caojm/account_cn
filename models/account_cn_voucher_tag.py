from odoo import fields, models


class AccountCnVoucherTag(models.Model):
    _name = "account.cn.voucher.tag"
    _description = "Account Voucher Tag"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    name = fields.Char(
        required=True,
    )
    color = fields.Integer()
