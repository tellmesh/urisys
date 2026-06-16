def register(rt):
    rt.register('kvm://{target}/display/query/info', 'python://urirdp_kvm.handlers:display_info', kind='query', operation='kvm.display.info')
    rt.register('kvm://{target}/monitor/{monitor}/query/screenshot', 'python://urirdp_kvm.handlers:screenshot', kind='query', operation='kvm.screenshot')
    rt.register('kvm://{target}/task/command/click-text', 'python://urirdp_kvm.handlers:click_text', kind='command', operation='kvm.click_text', approval='required', side_effects=True)
    rt.register('kvm://{target}/task/command/type-text', 'python://urirdp_kvm.handlers:type_text', kind='command', operation='kvm.type_text', approval='required', side_effects=True)
