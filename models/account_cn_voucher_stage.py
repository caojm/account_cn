from odoo import fields, models


class AccountCnVoucherStage(models.Model):
    _name = "account.cn.voucher.stage"
    _description = "Voucher Stage"
    _order = "sequence"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    code = fields.Char(
        required=True,
    )
    name = fields.Char()
    sequence = fields.Integer(
        required=True,
        default=10,
    )
    fold = fields.Boolean()
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("prepared", "Prepared"),
            ("checked", "Checked"),
            ("signed", "Signed"),
            ("posted", "Posted"),
        ],
        string="Status",
        copy=True,
        default="draft",
    )
    voucher_type_id = fields.Many2one(
        "account.cn.voucher.type",
    )
