from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountCnReportFolder(models.Model):
    _name = "account.cn.report.folder"
    _description = "Report Folder"

    name = fields.Char()
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.user.accounting_book_id.currency_id,
    )
    date_from = fields.Date(
        required=True,
    )
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    last_update = fields.Datetime()
    posted_only = fields.Boolean(
        default=False,
    )
    exact_match = fields.Boolean(
        default=False,
    )
    comparison = fields.Boolean(
        default=False,
    )
    com_date_from = fields.Date(
        string="Date From",
    )
    com_date_to = fields.Date(
        string="Date To",
    )
    accounting_book_ids = fields.Many2many(
        "account.cn.accounting.book",
        compute="_compute_accounting_book_ids",
        store=True,
        readonly=False,
        required=True,
        default=lambda self: self.env.user.accounting_book_id,
        domain="[('currency_id', '=', currency_id)]",
    )
    company_ids = fields.Many2many(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    folder_model_ids = fields.One2many(
        "account.cn.report.folder.model",
        "report_folder_id",
    )
    folder_checker_ids = fields.One2many(
        "account.cn.report.folder.checker",
        "report_folder_id",
    )

    @api.depends("currency_id")
    def _compute_accounting_book_ids(self):
        self.ensure_one()
        self.accounting_book_ids = self.accounting_book_ids.filtered(
            lambda r: r.currency_id == self.currency_id
        )

    def compute_and_check(self):
        pass

    def compute_only(self):
        report_item_classified = self._get_report_item_classified_by_measure()
        if report_item_classified["ob"]:
            pass
        if report_item_classified["cb"]:
            pass
        if report_item_classified["mob"]:
            pass
        if report_item_classified["yob"]:
            pass
        if report_item_classified["ca"]:
            pass
        if report_item_classified["cma"]:
            pass
        if report_item_classified["cya"]:
            pass
        self.last_update = fields.Datetime.now()

    def check_only(self):
        pass

    def to_be(self):
        pass

    def _get_report_item_classified_by_measure(self):
        report_item_classified = {}
        report_item_classified["ob"] = []
        report_item_classified["cb"] = []
        report_item_classified["mob"] = []
        report_item_classified["yob"] = []
        report_item_classified["ca"] = []
        report_item_classified["cma"] = []
        report_item_classified["cya"] = []
        for fm in self.folder_model_ids:
            for ri in fm.report_model_id.item_ids:
                if ri.measure == "ob":
                    report_item_classified["ob"].append(ri)
                elif ri.measure == "cb":
                    report_item_classified["cb"].append(ri)
                elif ri.measure == "mob":
                    report_item_classified["mob"].append(ri)
                elif ri.measure == "yob":
                    report_item_classified["yob"].append(ri)
                elif ri.measure == "ca":
                    report_item_classified["ca"].append(ri)
                elif ri.measure == "cma":
                    report_item_classified["cma"].append(ri)
                elif ri.measure == "cya":
                    report_item_classified["cya"].append(ri)
                else:
                    error_msg = _(
                        "The report item %s has a wrong measure.",
                        "(ID: " + str(ri.id) + ", Name: " + ri.name + ")",
                    )
                    raise UserError(error_msg)
        return report_item_classified
