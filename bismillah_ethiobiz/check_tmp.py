import frappe

def execute():
    s = frappe.get_doc('HADEEDA Settings')
    print('enabled:', s.enabled)
    print('inline_ai_enabled:', getattr(s, 'inline_ai_enabled', 'MISSING'))
    print('trigger_character:', getattr(s, 'trigger_character', 'MISSING'))
    print('All fields:', list(s.as_dict().keys()))
