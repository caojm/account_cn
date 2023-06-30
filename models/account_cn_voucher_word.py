from odoo import fields, models


class AccountCnVoucherWord(models.Model):
    _name = "account.cn.voucher.word"
    _description = "Account Voucher Type"


    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    name = fields.Char(required=True)

