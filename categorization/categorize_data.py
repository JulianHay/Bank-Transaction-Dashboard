def categorize_transaction(description, creditor_name):
    # Dictionary of categories and associated keywords
    categories = {
        "Travel": [
            "hotel", "flight", "travel", "uber", "train", "airline", "transport", "auto", "bus", "car", "taxi",
            "petrol", "4wd",
            "metro", "airport", "toll", "parking", "gasoline", "cruise", "rental car", "lyft", "subway",
            "hotel", "flug", "reise", "uber", "zug", "bahn", "flieger", "transport", "wagen", "benzin", "flughafen",
            "maut", "parken", "mietwagen", "bahnkarte", "reisebus"
        ],
        "Rent": [
            "rent", "lease", "apartment", "housing", "property", "mortgage", "tenant", "room", "sublet", "condo",
            "miete", "mietvertrag", "wohnung", "apartment", "wohnen", "pacht", "hypothek", "untermiete", "haus",
            "kaution", "immobilien", "hausgeld", "wohngebäude"
        ],
        "Utilities": [
            "electricity", "water", "internet", "gas", "utility", "phone", "cable", "tv", "trash", "sewage",
            "heating",
            "cooling", "power", "solar", "wifi", "broadband",
            "strom", "wasser", "internet", "gas", "nebenkosten", "müll", "abwasser", "heizung", "energie",
            "telefon",
            "kabel", "fernsehen", "solar", "telefonanschluss", "müllabfuhr", "aldimobile"
        ],
        "Entertainment": [
            "cinema", "movie", "concert", "music", "event", "show", "theater", "festival", "exhibition", "museum",
            "game",
            "amusement", "park", "bowling", "streaming", "netflix", "hulu", "spotify", "eventbrite",
            "kino", "film", "konzert", "musik", "veranstaltung", "theater", "festival", "ausstellung", "museum",
            "spiel", "freizeitpark", "oper"
        ],
        "Groceries": [
            "grocery", "supermarket", "store", "food", "market", "aldi", "woolworths", "coles", "bws", "fugly",
            "lidl",
            "rewe", "edeka", "bakery", "butcher", "farmers market", "whole foods", "costco", "target", "walmart",
            "tesco",
            "lebensmittel", "supermarkt", "geschäft", "essen", "markt", "einkaufen", "bäckerei", "metzger",
            "biomarkt",
            "dm", "rossmann", "kaufland", "futter", "nahrungsmittel"
        ],
        "Shopping": [
            "shop", "clothing", "fashion", "retail", "mall", "boutique", "shoes", "accessories", "electronics",
            "furniture", "amazon", "ebay", "apparel", "cosmetics", "jewelry", "department store", "zara", "hm",
            "etsy", "kmart", "bunnings",
            "kleidung", "mode", "handel", "einkaufen", "boutique", "schuhe", "accessoires", "elektronik", "möbel",
            "bekleidung", "kosmetik", "schmuck", "kaufhaus", "warenhaus"
        ],
        "Insurance": [
            "insurance", "health", "auto", "car", "home", "life", "property", "coverage", "policy", "premium",
            "dental",
            "vision", "travel insurance",
            "versicherung", "gesundheit", "hausrat", "leben", "haftpflicht", "krankenversicherung",
            "versicherungsschutz",
            "prämie", "dental", "rechtsschutz", "hausversicherung", "HanseMerkur", "medibank"
        ],
        "Healthcare": [
            "doctor", "hospital", "clinic", "medicine", "pharmacy", "prescription", "dental", "vision", "medical",
            "surgery", "therapy", "mental health", "optometrist", "orthodontist", "vaccination", "medication",
            "lab",
            "arzt", "krankenhaus", "klinik", "medizin", "apotheke", "rezept", "zahn", "optiker", "medizinisch",
            "chirurgie", "therapie", "psychotherapie", "vorsorge", "impfung", "medikation", "gesundheitswesen"
        ],
        "Trading & Investment": [
            "stocks", "crypto", "bitcoin", "investment", "forex", "broker", "shares", "mutual fund", "dividends",
            "wealth", "roth", "401k", "ira", "bond", "Konto", "kreditkarte", "kredit", "kreditkarte",
            "aktien", "etf", "zinsen", "geld", "sparbuch", "fonds", "börsenhandel", "krypto", "investition",
            "depot", "anteile", "dividende", "wohlstand", "wertpapier", "anleihe", "investor", "wise", "wp-order"
        ],
        "Eating Out": [
            "restaurant", "kaffee", "diner", "bistro", "brunch", "buffet", "grill", "pizzeria", "fast food",
            "takeaway", "coffee", "cafe",
            "delivery", "food truck", "cuisine", "fine dining", "food court",
            "kaffee", "bar", "pub", "biergarten", "kneipe", "bistro", "imbiss", "essen", "lieferdienst",
            "foodtruck",
            "gasthaus", "gastronomie", "feinschmecker", "bier", "bierkeller"
        ],
        "Subscriptions": [
            "membership", "subscription", "netflix", "spotify", "hulu", "apple", "prime", "amazon", "audible",
            "adobe", "office 365", "software", "cloud", "gaming", "newspaper", "magazine",
            "mitgliedschaft", "abo", "abonnement", "software", "dienst", "servicegebühr"
        ],
        "Sport & Fitness": [
            "tjoa", "gym", "fitness", "sports", "workout", "exercise", "membership", "yoga", "trainer", "coach", "swim",
            "run", "marathon", "race", "cycling", "crossfit", "pilates", "wellness", "health club",
            "fitness", "sport", "training", "mitgliedschaft", "yoga", "trainer", "coach", "schwimmen", "laufen",
            "rennen", "fahrrad", "gesundheitsclub", "studio", "freizeit", "marathon"
        ],
        "Education": [
            "school", "tuition", "university", "college", "course", "class", "training", "workshop", "seminar",
            "textbook", "online course", "exam", "certification", "degree", "learning", "edtech", "enrollment",
            "schule", "unterricht", "universität", "hochschule", "seminar", "fortbildung", "weiterbildung",
            "lehrgang", "studium", "prüfung", "zertifizierung", "abschluss", "studiengebühren", "lehrmaterial"
        ],
        "Charity & Donations": [
            "donation", "charity", "ngo", "fundraiser", "non-profit", "cause", "volunteer", "church", "temple",
            "mosque",
            "tithing", "contribution", "philanthropy", "gift", "pledge",
            "spende", "wohltätigkeit", "hilfsorganisation", "stiftung", "gemeinnützig", "kirche", "tempel",
            "moschee",
            "spendenaktion", "engagement", "philanthropie", "beitrag", "spendengeld"
        ],
        "Home Improvement": [
            "home depot", "lowes", "renovation", "furniture", "appliances", "hardware", "paint", "plumbing",
            "electrical",
            "landscaping", "garden", "tools", "decor", "carpentry", "remodel", "construction",
            "baumarkt", "renovierung", "möbel", "geräte", "werkzeug", "farbe", "sanitär", "elektrik",
            "landschaftsbau",
            "garten", "deko", "umbau", "hausausstattung", "tapeten", "fliesen"
        ],
        "Personal Care": [
            "salon", "spa", "massage", "haircut", "nails", "makeup", "skincare", "barber", "beauty", "cosmetic",
            "facial", "treatment", "self-care", "waxing", "tanning", "manicure", "pedicure",
            "friseur", "kosmetik", "nagelstudio", "friseursalon", "schönheitspflege", "hautpflege", "barbier",
            "wellness", "gesichtsbehandlung", "selbstpflege", "haar", "waxing", "sonnenstudio", "beauty"
        ],
        "Pets": [
            "pet", "vet", "pet food", "pet store", "pet care", "dog", "cat", "grooming", "supplies", "kennel",
            "boarding",
            "adoption", "animal clinic", "animal hospital",
            "haustier", "tierarzt", "tierfutter", "tierhandlung", "pflege", "hund", "katze", "haustierbedarf",
            "zubehör",
            "adoption", "tierbetreuung", "tierheim", "veterinär", "tierklinik", "haustierpflege"
        ],
        "Income": [
            "salary", "wage", "income", "payroll", "bonus", "commission", "stipend", "earnings",
            "income tax refund",
            "compensation", "reimbursement", "net pay", "gross pay",
            "gehalt", "lohn", "einkommen", "vergütung", "prämie", "kommission", "stipendium", "verdienst",
            "einkommenssteuererstattung", "brutto", "netto", "abrechnung", "monatsgehalt", "jahresgehalt"
        ],
        "Miscellaneous": [
            "misc", "other", "general", "uncategorized", "service charge", "bank fee", "penalty fee", "late fee",
            "fee collection", "sundries", "varied expenses",
            "divers", "sonstige", "allgemein", "unkategorisiert", "verschiedenes", "unbekannt", "ausgabe", "gebühr",
            "servicegebühr", "bankgebühr", "strafgebühr", "verspätungsgebühr", "gebührenerhebung", "sammelposten"
        ]
    }

    # Convert both fields to lowercase for easier matching
    description = description.lower()
    creditor_name = creditor_name.lower()

    # Check for keywords in each category for both fields
    for category, keywords in categories.items():
        if any(keyword in description for keyword in keywords) or any(
                keyword in creditor_name for keyword in keywords):
            return category

    # Default category if no keywords match
    return "Other"

def categorize_transactions(transactions):
    transactions_without_nan = transactions.fillna('')
    transactions['category'] = transactions_without_nan.apply(lambda row: categorize_transaction(row['description'], row['creditorName']), axis=1)
    return transactions