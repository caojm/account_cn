from odoo.tools import frozendict, formatLang, format_date, float_compare, Query
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountCnReportItem(models.Model):
    _name = "account.cn.report.item"
    _description = "Report Item"

    report_model_id = fields.Many2one(
        "account.cn.report.model",
        required=True,
    )
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
    aggregator_factor = fields.Boolean()
    factor_of_ids = fields.One2many(
        "account.cn.report.aggregator",
        "aggregator_factor_id",
    )
    position = fields.Selection(
        selection=[
            ("thead", "Table Head"),
            ("tbody", "Table Body"),
            ("tfoot", "Table Foot"),
        ],
        copy=True,
    )
    location = fields.Char()
    name = fields.Char()
    measure = fields.Selection(
        selection=[
            ("ob", "Opening Balance"),
            ("cb", "Closing Balance"),
            ("mob", "Month Opening Balance"),
            ("yob", "Year Opening Balance"),
            ("ca", "Current Amount"),
            ("cma", "Current Month Amount"),
            ("cya", "Current Year Amount"),
        ],
        copy=True,
        required=True,
        default="cb",
    )
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

    @api.constrains("aggregator_factor")
    def _check_circular_reference(self):
        for item in self:
            if not item.aggregator_factor and item.factor_of_ids:
                error_msg = _(
                    "The item %s is the factor of aggregator.",
                    str(item.id) + item.name,
                )
                raise UserError(error_msg)
