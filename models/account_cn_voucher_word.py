from odoo import fields, models


class AccountCnVoucherWord(models.Model):
    _name = "account.cn.voucher.word"
    _description = "Account Voucher Word"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    code = fields.Char(
        required=True,
    )
    name = fields.Char(
        required=True,
    )
    voucher_number_sequence_id = fields.Many2one(
        "ir.sequence",
        required=True,
        copy=False,
        domain="[('code', '=like', 'account_cn.%')]",
    )
