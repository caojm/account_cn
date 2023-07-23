from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountCnReportData(models.Model):
    _name = "account.cn.report.data"
    _description = "Report Data"

    report_folder_id = fields.Many2one(
        "account.cn.report.folder",
        required=True,
    )
    report_item_id = fields.Many2one(
        "account.cn.report.item",
        required=True,
    )
    report_model_id = fields.Many2one(
        related="report_item_id.report_model_id",
    )
    input = fields.Float(
        related="report_item_id.input",
    )
    filter_sum = fields.Float()
    aggregator_sum = fields.Float()
    final_data = fields.Float(
        compute="_compute_final_data",
    )
    comparison = fields.Boolean(
        default=False,
    )

    def to_be(self):
        pass

    @api.depends("input", "filter_sum", "aggregator_sum")
    def _compute_final_data(self):
        for r in self:
            if r.input:
                r.final_data = r.input
            else:
                r.final_data = r.filter_sum + r.aggregator_sum
