from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountCnReportCheckerLine(models.Model):
    _name = "account.cn.report.checker.line"
    _description = "Report Checker Line"

    name = fields.Char()
    report_item_id = fields.Many2one(
        "account.cn.report.item",
        required=True,
    )
    aggregation = fields.Selection(
        selection=[
            ("plus", "+"),
            ("minus", "-"),
        ],
        default="plus",
    )
