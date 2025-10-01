# === SKEW CONFIGURATION - EASY TO ADJUST ===
# This file controls the distribution skewing for creature types and sizes

SKEW_CONFIG = {
    # Subcategory distribution skew (higher = more uneven distribution)
    'subcategory_skew': 2.0,
    
    # Size distribution skew (higher = more extreme sizes)
    'size_skew': 1.001,
    
    # Specific size preferences (values > 1 favor that size, < 1 reduce it)
    'size_preferences': {
        'Tiny': 2.0,
        'Small': 1.75, 
        'Mid': 1.0,
        'Large': 0.7,
        'Giant': 0.4,
        'Mega': 0.2,
        'Super': 0.1
    },
    
    # Category preferences (values > 1 favor that category type)
    'category_preferences': {
        'Bird': 1.3589,
        'Amphibian': 1.2,
        'Vertebrate': 1.8,
        'Reptile': 1.4,
        'Fish': 1.55,
        'Invertebrate': 2.0
    }
}