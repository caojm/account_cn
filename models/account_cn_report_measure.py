from odoo import api, fields, models


class AccountCnReportMeasure(models.Model):
    _name = "account.cn.report.measure"
    _description = "Report Measure"

    code = fields.Char(
        required=True,
    )
    name = fields.Char()
