from odoo import fields, models


class AccountCnVoucherType(models.Model):
    _name = "account.cn.voucher.type"
    _description = "Voucher Type"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    code = fields.Char(
        required=True,
    )
    name = fields.Char()
    voucher_stage_ids = fields.One2many(
        "account.cn.voucher.stage",
        "voucher_type_id",
        copy=True,
    )
