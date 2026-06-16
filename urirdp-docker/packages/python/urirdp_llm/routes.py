def register(rt):
    rt.register('llm://{target}/vision/query/analyze', 'python://urirdp_llm.handlers:analyze', kind='query', operation='llm.vision.analyze')
