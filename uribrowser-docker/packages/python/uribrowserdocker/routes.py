def register(runtime):
    runtime.register('browser://{session}/query/status', 'python://uribrowserdocker.handlers:status', kind='query', operation='browser.status')
    runtime.register('browser://{session}/page/command/open', 'python://uribrowserdocker.handlers:open_page', kind='command', operation='browser.page.open', approval='required', side_effects=True)
    runtime.register('browser://{session}/page/query/dom', 'python://uribrowserdocker.handlers:get_dom', kind='query', operation='browser.page.dom')
    runtime.register('browser://{session}/page/command/screenshot', 'python://uribrowserdocker.handlers:screenshot', kind='command', operation='browser.page.screenshot', approval='required', side_effects=True)
