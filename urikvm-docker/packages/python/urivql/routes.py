def register(runtime):
    runtime.register(
        "vql://{host}/ui/latest/query/detect",
        "python://urivql.handlers:ui_detect",
        kind="query",
        operation="vql.ui.detect",
    )
    runtime.register(
        "vql://{host}/ui/latest/query/compare",
        "python://urivql.handlers:ui_compare",
        kind="query",
        operation="vql.ui.compare",
    )
