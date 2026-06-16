def register(rt):
    rt.register('him://{target}/mouse/command/move', 'python://urirdp_him.handlers:mouse_move', kind='command', operation='him.mouse.move', approval='required', side_effects=True)
    rt.register('him://{target}/mouse/command/click', 'python://urirdp_him.handlers:mouse_click', kind='command', operation='him.mouse.click', approval='required', side_effects=True)
    rt.register('him://{target}/keyboard/command/type', 'python://urirdp_him.handlers:keyboard_type', kind='command', operation='him.keyboard.type', approval='required', side_effects=True)
    rt.register('him://{target}/keyboard/command/type-text', 'python://urirdp_him.handlers:keyboard_type_text', kind='command', operation='him.keyboard.type_text', approval='required', side_effects=True)
    rt.register('him://{target}/keyboard/command/key', 'python://urirdp_him.handlers:keyboard_key', kind='command', operation='him.keyboard.key', approval='required', side_effects=True)
    rt.register('him://{target}/keyboard/command/hotkey', 'python://urirdp_him.handlers:keyboard_hotkey', kind='command', operation='him.keyboard.hotkey', approval='required', side_effects=True)
