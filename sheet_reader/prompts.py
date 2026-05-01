# sheet_reader/prompts.py
# Predefined prompts for the sheet reader module.
sheet_reader_prompts = {
    "my_holdings_analysis": (
        "Analyze my current stock holdings from the perspective of a short-period trader "
        "with a holding horizon of a few weeks. For each relevant holding, evaluate both "
        "positive and negative news, near-term trends, momentum, and catalysts that could "
        "affect the stock over the next several weeks. Explain the bullish and bearish case "
        "for each position, assess whether the current setup supports continuing to hold or "
        "exiting the position, and give a clear suggestion for each holding: hold, reduce, "
        "or exit. Prioritize practical short-term trading judgment over long-term investing "
        "theory. Include links to all references you use, and include publication dates for "
        "news or research sources."
    ),
}
