def register(rt):
    rt.register('llm://{target}/vision/query/analyze', 'python://urirdp_llm.handlers:analyze', kind='query', operation='llm.vision.analyze')
    rt.register('llm://{target}/text/query/decide', 'python://urirdp_llm.handlers:decide', kind='query', operation='llm.text.decide')
    rt.register('llm://{target}/text/query/plan', 'python://urirdp_llm.handlers:plan', kind='query', operation='llm.text.plan')
