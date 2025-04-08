# Chelsea squads grouped by type
squad_groups = {
    "Senior": [
        {"id": "palmer", "name": "Cole Palmer", "position": "Forward", "number": 20},
        {"id": "jackson", "name": "Nicolas Jackson", "position": "Forward", "number": 15},
        {"id": "mudryk", "name": "Mykhailo Mudryk", "position": "Forward", "number": 10},
        {"id": "reece", "name": "Reece James", "position": "Defender", "number": 24},
        {"id": "chilwell", "name": "Ben Chilwell", "position": "Defender", "number": 21},
        {"id": "enzo", "name": "Enzo Fernández", "position": "Midfielder", "number": 8},
        {"id": "caicedo", "name": "Moisés Caicedo", "position": "Midfielder", "number": 25},
        {"id": "sanchez", "name": "Robert Sánchez", "position": "Goalkeeper", "number": 1},
    ],
    "U21s": [
        {"id": "hall", "name": "Lewis Hall", "position": "Defender", "number": 67},
        {"id": "wareham", "name": "George Wareham", "position": "Forward", "number": 68},
    ],
    "FA Youth Cup": [
        {"id": "brooking", "name": "Leo Brooking", "position": "Midfielder", "number": 70},
    ],
    "U18s": [
        {"id": "watson", "name": "Ethan Watson", "position": "Defender", "number": 72},
    ],
    "On Loan": [
        {"id": "lukaku", "name": "Romelu Lukaku", "position": "Forward", "number": 90},
    ],
    "Staff": [
        {"id": "poch", "name": "Mauricio Pochettino", "position": "Staff", "number": ""},
    ]
}

# Opposition teams structured the same way for flexibility
opposition_groups = {
    "Senior": {
        "Premier League": {
            "Arsenal": [{"id": "palmer", "name": "Cole Palmer", "position": "Forward", "number": 20}],
            "Man City": [...],
        },
        "Champions League": {
            "PSG": [...],
            "Real Madrid": [...],
        }
    },
    "U21s": {
        "Premier League 2": {
            "Arsenal U21s": [...],
            "Spurs U21s": [...],
        }
    },
    "U18s": {
        "U18 Premier League": {
            "Liverpool U18s": [...],
            "Man United U18s": [...],
        }
    }
}

