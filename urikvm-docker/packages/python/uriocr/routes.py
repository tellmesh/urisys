def register(runtime):
    runtime.register('ocr://{host}/image/latest/query/text', 'python://uriocr.handlers:latest_text', kind='query', operation='ocr.latest.text')
    runtime.register('ocr://{host}/image/{image_id}/query/text', 'python://uriocr.handlers:image_text', kind='query', operation='ocr.image.text')
