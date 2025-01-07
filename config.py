import pygame

# Window dimensions
WIDTH = 1024
HEIGHT = 768

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (128, 128, 128)

# Game settings
FPS = 60
SAVE_FILE = "save_data.json"

# Difficulty settings
DIFFICULTY_SETTINGS = {
    "Easy": {"disaster_chance": 0.0005, "customer_order_chance": 0.001, "bakecoin_multiplier": 1.5},
    "Normal": {"disaster_chance": 0.001, "customer_order_chance": 0.0005, "bakecoin_multiplier": 1.0},
    "Hard": {"disaster_chance": 0.002, "customer_order_chance": 0.00025, "bakecoin_multiplier": 0.75}
}

# Base ingredients
base_ingredients = ["Flour", "Sugar", "Eggs", "Milk", "Butter", "Cocoa", "Vanilla", "Baking Powder", "Powdered Sugar"]

# Sound configuration
DEFAULT_VOLUMES = {
    'master': 0.8,
    'mixing': 0.4,
    'baking': 0.3,
    'effects': 0.5,
    'ambient': 0.1
}

# Sound variations for different ingredient types
INGREDIENT_SOUNDS = {
    'dry': {
        'pour': [
            'mixing/pour_flour.wav',
            'mixing/pour_sugar.wav',
            'mixing/pour_cocoa.wav'
        ],
        'impact': [
            'mixing/flour_impact.wav',
            'mixing/sugar_impact.wav'
        ]
    },
    'liquid': {
        'pour': [
            'mixing/pour_milk.wav',
            'mixing/pour_vanilla.wav',
            'mixing/pour_eggs.wav'
        ],
        'splash': [
            'mixing/liquid_splash1.wav',
            'mixing/liquid_splash2.wav'
        ]
    },
    'soft': {
        'pour': [
            'mixing/scoop_butter.wav',
            'mixing/scoop_frosting.wav'
        ],
        'impact': [
            'mixing/soft_impact1.wav',
            'mixing/soft_impact2.wav'
        ]
    },
    'solid': {
        'pour': [
            'mixing/pour_chips.wav',
            'mixing/pour_nuts.wav'
        ],
        'impact': [
            'mixing/chips_impact.wav',
            'mixing/solid_impact.wav'
        ]
    }
}

# Mixing process sounds
MIXING_SOUNDS = {
    'start': 'mixing/mix_start.wav',
    'loop': 'mixing/mix_loop.wav',
    'end': 'mixing/mix_end.wav',
    'sparkle': [
        'effects/sparkle1.wav',
        'effects/sparkle2.wav',
        'effects/sparkle3.wav'
    ]
}

# Baking process sounds
BAKING_SOUNDS = {
    'start': 'baking/oven_start.wav',
    'loop': 'baking/oven_loop.wav',
    'bubble': [
        'baking/bubble1.wav',
        'baking/bubble2.wav',
        'baking/bubble3.wav'
    ],
    'steam': [
        'baking/steam1.wav',
        'baking/steam2.wav'
    ],
    'sizzle': 'baking/sizzle_loop.wav',
    'ding': 'baking/ding.wav'
}

# Ambient sounds
AMBIENT_SOUNDS = {
    'kitchen': 'ambient/kitchen_loop.wav',
    'oven_hum': 'ambient/oven_hum.wav',
    'clock_tick': 'ambient/clock_tick.wav'
}

# Sound specifications
AUDIO_SPECS = {
    'format': 'wav',
    'sample_rate': 44100,
    'channels': 2,  # Stereo
    'bit_depth': 16
}
