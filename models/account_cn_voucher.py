from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError


class AccountCnVoucher(models.Model):
    _name = "account.cn.voucher"
    _description = "Accounting Voucher"
    _check_company_auto = True

    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    company_currency_id = fields.Many2one(
        string="Company Currency",
        related="company_id.currency_id",
        readonly=True,
    )
    accounting_book_id = fields.Many2one(
        "account.cn.accounting.book",
        required=True,
        default=lambda self: self.env.user.accounting_book_id,
        check_company=True,
    )
    book_currency_id = fields.Many2one(
        string="Accounting Book Currency",
        related="accounting_book_id.currency_id",
    )
    date = fields.Date(
        default=fields.Date.today,
        required=True,
        states={
            "posted": [("readonly", True)],
            "cancel": [("readonly", True)],
        },
        copy=False,
    )
    word_id = fields.Many2one(
        "account.cn.voucher.word",
        required=True,
        default=lambda self: self.env.user.voucher_word_id,
        check_company=True,
    )
    voucher_type_id = fields.Many2one(
        "account.cn.voucher.type",
        required=True,
        default=lambda self: self.env.user.voucher_type_id,
    )
    number = fields.Integer(
        compute="_compute_number",
        store=True,
        readonly=False,
    )
    attachment = fields.Integer()
    stage_id = fields.Many2one(
        "account.cn.voucher.stage",
        compute="_compute_stage_id",
        store=True,
        readonly=False,
        group_expand="_group_expand_stage_id",
        domain="[('voucher_type_id', '=', voucher_type_id)]",
    )
    first_stage = fields.Many2one(
        "account.cn.voucher.stage",
        compute="_compute_first_stage",
    )
    is_first_stage = fields.Boolean(
        compute="_compute_first_stage",
    )
    state = fields.Selection(
        related="stage_id.state",
        string="Status",
    )
    next_state = fields.Char(
        compute="_compute_next_state",
    )
    amount_total = fields.Monetary(
        string="Amount",
        compute="_compute_amount",
        # store=True,
        # readonly=True,
        currency_field="book_currency_id",
    )
    line_ids = fields.One2many(
        "account.cn.voucher.line",
        "voucher_id",
        string="Entries",
        copy=True,
    )
    include_cash_flow = fields.Boolean(
        compute="_compute_include_cash_flow",
    )
    accounting_supervisor_id = fields.Many2one(
        related="accounting_book_id.accounting_supervisor_id",
    )
    poster_id = fields.Many2one(
        "res.users",
        readonly=True,
        copy=False,
    )
    casher_id = fields.Many2one(
        "res.users",
        readonly=True,
        copy=False,
    )
    checker_id = fields.Many2one(
        "res.users",
        readonly=True,
        copy=False,
    )
    preparer_id = fields.Many2one(
        "res.users",
        readonly=True,
        copy=False,
    )

    @api.depends(
        "line_ids.currency_id",
        "line_ids.debit",
        "line_ids.credit",
    )
    def _compute_amount(self):
        for voucher in self:
            amount_total = 0.0
            for line in voucher.line_ids:
                amount_total += line.debit
            voucher.amount_total = amount_total

    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s-%s (%s)" % (record.word_id.name, record.number, record.date)
            result.append((record.id, rec_name))
        return result

    @api.depends(
        "date",
        "word_id",
    )
    def _compute_number(self):
        seq = self.word_id.voucher_number_sequence_id._get_current_sequence(self.date)
        if seq:
            self.number = seq.number_next_actual

    def do_next_stage(self):
        for voucher in self:
            if voucher.stage_id:
                stages = voucher._stage_find(
                    voucher.voucher_type_id.id,
                    domain=[("sequence", ">=", voucher.stage_id.sequence)],
                    limit=2,
                )
                if len(stages) == 2:
                    voucher.stage_id = stages[1]
                    voucher._set_signature()
                else:
                    continue

    def undo_next_stage(self):
        for voucher in self:
            if voucher.stage_id:
                stages = voucher._stage_find(
                    voucher.voucher_type_id.id,
                    order="sequence desc, id desc",
                    domain=[("sequence", "<=", voucher.stage_id.sequence)],
                    limit=2,
                )
                if len(stages) == 2:
                    voucher._unset_signature()
                    voucher.stage_id = stages[1]
                else:
                    continue

    def reject_stage(self):
        for voucher in self:
            voucher.stage_id = voucher.first_stage
            voucher.preparer_id = False
            voucher.checker_id = False
            voucher.casher_id = False
            voucher.poster_id = False

    def _stage_find(
        self, voucher_type_id=False, domain=None, order="sequence, id", limit=1
    ):
        if voucher_type_id:
            search_domain = [("voucher_type_id", "=", voucher_type_id)]
        if domain:
            search_domain += domain
        return self.env["account.cn.voucher.stage"].search(
            search_domain, order=order, limit=limit
        )

    def _set_signature(self):
        for voucher in self:
            if voucher.stage_id.state == "prepared":
                voucher.preparer_id = self.env.user
            elif voucher.stage_id.state == "checked":
                voucher.checker_id = self.env.user
            elif voucher.stage_id.state == "signed":
                voucher.casher_id = self.env.user
            elif voucher.stage_id.state == "posted":
                voucher.poster_id = self.env.user
            else:
                continue

    def _unset_signature(self):
        for voucher in self:
            if voucher.stage_id.state == "prepared":
                voucher.preparer_id = False
            elif voucher.stage_id.state == "checked":
                voucher.checker_id = False
            elif voucher.stage_id.state == "signed":
                voucher.casher_id = False
            elif voucher.stage_id.state == "posted":
                voucher.poster_id = False
            else:
                continue

    @api.depends("voucher_type_id")
    def _compute_stage_id(self):
        for voucher in self:
            if voucher.voucher_type_id:
                if voucher.voucher_type_id != voucher.stage_id.voucher_type_id:
                    voucher.stage_id = voucher._stage_find(
                        voucher.voucher_type_id.id, [("fold", "=", False)]
                    )
            else:
                voucher.stage_id = False

    def _group_expand_stage_id(self, stages, domain, order):
        print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
        print(self)
        print(stages)
        print(domain)
        print(order)
        dm = [
            (
                "id",
                "in",
                [
                    self.env.ref("account_cn.stage_draft").id,
                    self.env.ref("account_cn.stage_prepared").id,
                    self.env.ref("account_cn.stage_checked").id,
                    self.env.ref("account_cn.stage_signed").id,
                    self.env.ref("account_cn.stage_posted").id,
                ],
            )
        ]
        print(dm)
        return stages.search(dm, order=order)

    @api.depends("stage_id")
    def _compute_next_state(self):
        for voucher in self:
            if voucher.stage_id:
                stages = voucher._stage_find(
                    voucher.voucher_type_id.id,
                    domain=[("sequence", ">=", voucher.stage_id.sequence)],
                    limit=2,
                )
                voucher.next_state = stages[1].state if len(stages) == 2 else False
            else:
                voucher.next_state = None

    @api.depends("voucher_type_id.voucher_stage_ids.sequence")
    def _compute_first_stage(self):
        for voucher in self:
            if voucher.voucher_type_id and voucher.voucher_type_id.voucher_stage_ids:
                voucher.first_stage = voucher._stage_find(voucher.voucher_type_id.id)
                voucher.is_first_stage = (
                    True if voucher.stage_id == voucher.first_stage else False
                )
            else:
                voucher.is_first_stage = None

    @api.depends("line_ids")
    def _compute_include_cash_flow(self):
        for voucher in self:
            cash = False
            not_cash = False
            for line in voucher.line_ids:
                if cash and not_cash:
                    break
                elif line.account_id.account_type == "asset_cash":
                    cash = True
                elif line.account_id.account_type not in ("asset_cash", "off_balance"):
                    not_cash = True
                else:
                    continue
            if cash and not_cash:
                voucher.include_cash_flow = True
            else:
                voucher.include_cash_flow = False

    @api.model
    def create(self, vals):
        new_record = super().create(vals)
        new_record.number = new_record.word_id.voucher_number_sequence_id.next_by_id(
            new_record.date
        )
        return new_record

    def write(self, vals):
        if "word_id" in vals or "date" in vals:
            Word = self.env["account.cn.voucher.word"]
            old_seq = self.word_id.voucher_number_sequence_id._get_current_sequence(
                self.date
            )
            new_seq = Word.browse(
                vals.get("word_id", self.word_id.id)
            ).voucher_number_sequence_id._get_current_sequence(
                vals.get("date", self.date)
            )
            if new_seq != old_seq:
                vals["number"] = new_seq.sequence_id.next_by_id(
                    vals.get("date", self.date)
                )
            else:
                vals["number"] = self.number
        super().write(vals)

    @api.constrains("line_ids")
    def _check_balanced(self):
        for voucher in self:
            balance = sum(voucher.line_ids.mapped("debit")) - sum(
                voucher.line_ids.mapped("credit")
            )
            if balance:
                error_msg = _("The voucher %s is not balanced.", voucher.display_name)
                raise UserError(error_msg)

    @api.constrains("line_ids")
    def _check_entry_count(self):
        for voucher in self:
            count = len(voucher.line_ids)
            if count < 2:
                error_msg = _(
                    "Two or more entries of voucher %s is needed.", voucher.display_name
                )
                raise UserError(error_msg)
