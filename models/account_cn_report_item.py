from odoo.tools import frozendict, formatLang, format_date, float_compare, Query
from odoo import api, fields, models


class AccountCnReportItem(models.Model):
    _name = "account.cn.report.item"
    _description = "Report Item"

    report_model_id = fields.Many2one("account.cn.report.model")
    company_id = fields.Many2one(
        related="report_model_id.company_id",
        store=True,
        readonly=True,
        precompute=True,
    )
    report_model_code = fields.Char(
        related="report_model_id.code",
        store=True,
        copy=False,
        string="Report Model Code",
    )

    code = fields.Char(
        required=True,
    )
    name = fields.Char()
    measure_id = fields.Many2one("account.cn.report.measure")
    comment = fields.Char()
    filter_ids = fields.Many2many("account.cn.report.filter")
    input = fields.Float()
