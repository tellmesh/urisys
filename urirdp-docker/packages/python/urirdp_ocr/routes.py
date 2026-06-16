def register(rt):
    rt.register('ocr://{target}/image/latest/query/text', 'python://urirdp_ocr.handlers:latest_text', kind='query', operation='ocr.latest_text')
    rt.register('ocr://{target}/image/{image}/query/text', 'python://urirdp_ocr.handlers:image_text', kind='query', operation='ocr.image_text')
