{
    "name": "Chinese Accounting",
    "version": "1.0",
    "depends": ["base", "account"],
    "author": "Cao Jiaming",
    "category": "Category",
    "description": """
    Chinese Accounting
    """,
    # data files always loaded at installation
    "data": [
        # 'views/mymodule_view.xml',
        "security/ir.model.access.csv",
        "views/account_cn_voucher_views.xml",
        "views/account_cn_voucher_word_views.xml",
        "views/account_cn_voucher_type_views.xml",
        "views/account_cn_voucher_stage_views.xml",
        "views/account_cn_voucher_tag_views.xml",
        "views/account_cn_voucher_line_views.xml",
        "views/account_cn_accounting_book_views.xml",
        "views/res_company_views.xml",
        "views/res_users_views.xml",
        "views/ir_sequence_date_range_views.xml",
        "report/account_cn_voucher_reports.xml",
        "report/account_cn_voucher_templates.xml",
        "report/account_cn_subsidiary_ledger_reports.xml",
        "report/account_cn_subsidiary_ledger_templates.xml",
        "report/account_cn_general_ledger_reports.xml",
        "report/account_cn_general_ledger_templates.xml",
        "report/account_cn_account_balance_reports.xml",
        "report/account_cn_account_balance_templates.xml",
        "wizard/subsidiary_ledger_wizard_view.xml",
        "wizard/general_ledger_wizard_view.xml",
        "wizard/account_balance_wizard_view.xml",
        "wizard/renumber_voucher_wizard_view.xml",
        "views/account_cn_menus.xml",
        "data/account_cn_voucher_stage.xml",
    ],
    # data files containing optionally loaded demonstration data
    "demo": [
        # 'demo/demo_data.xml',
    ],
    "application": True,
}
