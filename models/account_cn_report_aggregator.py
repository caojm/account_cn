from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountCnReportAggregator(models.Model):
    _name = "account.cn.report.aggregator"
    _description = "Report Aggregator"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    aggregation = fields.Selection(
        selection=[
            ("plus", "+"),
            ("minus", "-"),
        ],
        required=True,
        default="plus",
    )
    aggregator_factor_id = fields.Many2one(
        "account.cn.report.item",
        domain="[('aggregator_factor', '=', True)]",
    )
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
        default="neq",
    )
    parent_item_id = fields.Many2one(
        "account.cn.report.item",
        required=True,
    )
    child_item_ids = fields.One2many(
        "account.cn.report.item",
        "parent_aggregator_id",
    )
    name = fields.Char()

    @api.constrains("parent_item_id")
    def _check_circular_reference(self):
        pool = set()
        pool.add(self)
        parent_agg = self.parent_item_id.parent_aggregator_id
        while parent_agg:
            if parent_agg in pool:
                error_msg = _(
                    "The aggregator %s has a circular referrence.",
                    parent_agg.name,
                )
                raise UserError(error_msg)
            else:
                pool.add(parent_agg)
                parent_agg = parent_agg.parent_item_id.parent_aggregator_id
