from odoo.tools import frozendict, formatLang, format_date, float_compare, Query
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountCnReportItem(models.Model):
    _name = "account.cn.report.item"
    _description = "Report Item"

    report_model_id = fields.Many2one("account.cn.report.model")
    company_id = fields.Many2one(
        related="report_model_id.company_id",
        store=True,
        readonly=True,
    )
    report_model_code = fields.Char(
        related="report_model_id.code",
        store=True,
        copy=False,
    )

    code = fields.Char(
        required=True,
    )
    name = fields.Char()
    measure_id = fields.Many2one("account.cn.report.measure")
    comment = fields.Char()
    filter_ids = fields.Many2many("account.cn.report.filter")
    input = fields.Float()
    parent_aggregator_id = fields.Many2one("account.cn.report.aggregator")
    child_aggregator_ids = fields.One2many(
        "account.cn.report.aggregator",
        "parent_item_id",
    )

    @api.constrains("parent_aggregator_id")
    def _check_circular_reference(self):
        pool = set()
        pool.add(self)
        parent_item = self.parent_aggregator_id.parent_item_id
        while parent_item:
            if parent_item in pool:
                error_msg = _(
                    "The item %s has a circular referrence.",
                    parent_item.code + parent_item.name,
                )
                raise UserError(error_msg)
            else:
                pool.add(parent_item)
                parent_item = parent_item.parent_aggregator_id.parent_item_id
