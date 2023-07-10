from odoo import api, models, fields


class User(models.Model):
    _inherit = ["res.users"]

    accounting_book_id = fields.Many2one(
        "account.cn.accounting.book",
    )
    voucher_type_id = fields.Many2one(
        "account.cn.voucher.type",
    )
    voucher_word_id = fields.Many2one(
        "account.cn.voucher.word",
    )
