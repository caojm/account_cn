from odoo import api, fields, models


class ResCompany(models.Model):
    _name = "res.company"
    _inherit = ["res.company"]

    default_book_id = fields.Many2one(
        "account.cn.accounting.book",
    )
