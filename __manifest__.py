{
    'name': "Chinese Accounting",
    'version': '1.0',
    'depends': ['base', 'account'],
    'author': "Cao Jiaming",
    'category': 'Category',
    'description': """
    Chinese Accounting
    """,
    # data files always loaded at installation
    'data': [
        # 'views/mymodule_view.xml',
        'security/ir.model.access.csv',
        'views/account_cn_voucher_views.xml',
        'views/account_cn_voucher_word_views.xml',
        'views/account_cn_voucher_line_views.xml',
        'views/account_cn_report_filter_views.xml',
        'views/account_cn_report_item_views.xml',
        'views/account_cn_report_model_views.xml',
        'views/account_cn_report_measure_views.xml',
        'views/account_cn_accounting_book_views.xml',
        'views/account_cn_menus.xml',
        'report/account_cn_voucher_reports.xml',
        'report/account_cn_voucher_templates.xml',
        'report/account_cn_subsidiary_ledger_reports.xml',
        'report/account_cn_subsidiary_ledger_templates.xml',
        'report/account_cn_balance_sheet_reports.xml',
        'report/account_cn_balance_sheet_templates.xml',
        'wizard/subsidiary_ledger_wizard_view.xml',
        'wizard/balance_sheet_wizard_view.xml',
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
        # 'demo/demo_data.xml',
    ],
    'application': True,
}
