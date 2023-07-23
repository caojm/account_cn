from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountCnReportChecker(models.Model):
    _name = "account.cn.report.checker"
    _description = "Report Checker"

    name = fields.Char()
    constant = fields.Float(
        default=0.0,
    )
    method = fields.Selection(
        selection=[
            ("gt", "Greater Than"),
            ("gte", "Greater Than  Or Equal To"),
            ("eq", "Equal To"),
            ("lse", "Less Than Or Equal"),
            ("ls", "Less Than"),
            ("neq", "Not Equal To"),
        ],
        required=True,
        default="eq",
    )
    left_line_ids = fields.Many2many(
        "account.cn.report.checker.line",
        "report_checker_left",
    )
    right_line_ids = fields.Many2many(
        "account.cn.report.checker.line",
        "report_checker_right",
    )
    checker_factor_ids = fields.Many2many(
        "account.cn.report.checker.line",
        "report_checker_precondition",
    )
