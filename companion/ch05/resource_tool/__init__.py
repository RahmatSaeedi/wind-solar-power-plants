"""resource_tool - the Plant P resource-analysis package of chapter 5.

    python -m companion.ch05.resource_tool validate-raw [logger.csv]
    python -m companion.ch05.resource_tool run companion/ch05/config/run_S0.yml
    python -m companion.ch05.resource_tool report companion/ch05/output/S0

Modules: rawdata (logger files), model (pure calculations), run (configured
run with recorded provenance), report (Markdown report), cli (commands).
Educational software for the fictional Plant P; never connect it to a plant.
"""
__version__ = "1.0.0"
