def register(rt):
    rt.register('rdp://{target}/session/query/status', 'python://urirdp.handlers:status', kind='query', operation='rdp.status')
    rt.register('rdp://{target}/session/query/display', 'python://urirdp.handlers:display', kind='query', operation='rdp.display')
    rt.register('rdp://{target}/display/query/status', 'python://urirdp.handlers:display_status', kind='query', operation='rdp.display.status')
    rt.register(
        'rdp://{target}/session/command/prepare-target',
        'python://urirdp.handlers:prepare_target',
        kind='command',
        operation='rdp.prepare_target',
        approval='required',
        side_effects=True,
    )
