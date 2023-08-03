from odoo import fields, models


class AccountCnVoucherWord(models.Model):
    _name = "account.cn.voucher.word"
    _check_company_auto = True
    _description = "Voucher Word"

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
    voucher_number_sequence_id = fields.Many2one(
        "ir.sequence",
        check_company=True,
        required=True,
        copy=False,
        domain="[('code', '=like', 'account_cn.%'), ('company_id', '=', company_id)]",
    )
