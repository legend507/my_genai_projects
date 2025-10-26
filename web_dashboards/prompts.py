url_resources = {
    # Money supply metrics, M1 is the most liquid measure. M2 and M3 are also available but I decided that they are less relevant.
    # This metric should tell me if most US people have money to spend/invest, which can cause speculation and meme stock rallies.
    "us_m1_dashboard": "https://fred.stlouisfed.org/series/M1SL",

    # US Congress members discloses their stock trades (not real time though).
    # Multiple sources available, but they somewhat give different data.
    # "Quiver Quants Congress Trading Dashboard": "https://www.quiverquant.com/congresstrading/",

    "prompts":"Based on the urls provided, tell me which US Congress member traded which stocks and when. Summarize the results in 2 tables organized bought and sould. Here are the urls: ",
    "well_known_politicians": [
        # Ron Wyden
        "https://www.quiverquant.com/congresstrading/politician/Ron%20Wyden-W000779",
        # Mark E. Green
        "https://www.quiverquant.com/congresstrading/politician/Mark%20E.%20Green-G000590?",
        # Josh Gottheimer
        "https://www.quiverquant.com/congresstrading/politician/Josh%20Gottheimer-G000583",
        # Michael T. McCaul
        "https://www.quiverquant.com/congresstrading/politician/Michael%20T.%20McCaul-M001157",
        # Debbie Wasserman Schultz
        "https://www.quiverquant.com/congresstrading/politician/Debbie%20Wasserman%20Schultz-W000797",
        # Roger Williams
        "https://www.quiverquant.com/congresstrading/politician/Roger%20Williams-W000816",
    ]
    # "Capitol Trades Dashboard": "https://www.capitoltrades.com/",
    # "InsiderFinance Congress Trading Dashboard": "https://www.insiderfinance.io/congress-trades",
}
