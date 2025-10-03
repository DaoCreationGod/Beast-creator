import os
import re
import random
import datetime
import logging
import sys
import math
import time
from collections import defaultdict
import json
from datetime import timedelta

# === FILE SIZE CONFIGURATION ===
MAX_FILE_SIZE_MB = 90  # CHANGE THIS NUMBER TO WHATEVER YOU WANT
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# === ENHANCED ETA TRACKING CLASS ===
class CreatureETA:
    def __init__(self, total_creatures):
        self.total_creatures = total_creatures
        self.start_time = time.time()
        self.creatures_completed = 0
        self.recent_times = []
        self.window_size = 100
        self.eta_history = []
        self.final_actual_time = None
        self.last_progress_display = 0
        
    def update(self, creatures_completed):
        """Update ETA calculation and store prediction"""
        self.creatures_completed = creatures_completed
        
        if creatures_completed > 0:
            current_time = time.time()
            elapsed = current_time - self.start_time
            
            # Calculate current rate
            creatures_per_second = creatures_completed / elapsed
            remaining_creatures = self.total_creatures - creatures_completed
            
            if creatures_per_second > 0:
                eta_seconds = remaining_creatures / creatures_per_second
            else:
                eta_seconds = 0
                
            eta_time = datetime.datetime.now() + datetime.timedelta(seconds=eta_seconds)
            percentage = (creatures_completed / self.total_creatures) * 100
            
            # Store this prediction for later accuracy calculation
            prediction = {
                'timestamp': current_time,
                'completion_percentage': percentage,
                'predicted_remaining_seconds': eta_seconds,
                'predicted_total_seconds': elapsed + eta_seconds,
                'actual_elapsed_so_far': elapsed
            }
            self.eta_history.append(prediction)
            
            return {
                'eta_time': eta_time.strftime("%H:%M:%S"),
                'eta_duration': str(timedelta(seconds=int(eta_seconds))),
                'elapsed': str(timedelta(seconds=int(elapsed))),
                'percentage': percentage,
                'rate_per_second': creatures_per_second,
                'rate_per_hour': creatures_per_second * 3600,
                'remaining': remaining_creatures
            }
        return None
    
    def display_progress(self, force_display=False):
        """Display a beautiful progress visualization"""
        current_time = time.time()
        
        # Only display progress every 30 seconds or when forced
        if not force_display and (current_time - self.last_progress_display < 30):
            return
            
        self.last_progress_display = current_time
        eta_info = self.update(self.creatures_completed)
        
        if not eta_info:
            return
            
        progress = self.creatures_completed / self.total_creatures
        bar_length = 40
        filled_length = int(bar_length * progress)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Clear line and display progress
        print('\r' + ' ' * 100, end='')  # Clear line
        print(f'\r🚀 Progress: {bar} {eta_info["percentage"]:.1f}%', end='')
        print(f' | 🕐 ETA: {eta_info["eta_time"]} ({eta_info["eta_duration"]})', end='')
        print(f' | 📊 {self.creatures_completed:,}/{self.total_creatures:,}', end='')
        print(f' | 🏃 {eta_info["rate_per_hour"]:,.0f}/hour', end='', flush=True)
    
    def finalize(self, actual_total_seconds):
        """Calculate final accuracy when process completes"""
        self.final_actual_time = actual_total_seconds
        final_accuracy = {}
        
        # Calculate accuracy for predictions at different completion percentages
        checkpoints = [10, 25, 50, 75]
        for checkpoint in checkpoints:
            checkpoint_predictions = [p for p in self.eta_history 
                                    if p['completion_percentage'] >= checkpoint - 2 and p['completion_percentage'] <= checkpoint + 2]
            if checkpoint_predictions:
                pred = checkpoint_predictions[0]
                accuracy_pct = (actual_total_seconds / pred['predicted_total_seconds'] - 1) * 100
                final_accuracy[f"{checkpoint}%"] = accuracy_pct
        
        return final_accuracy

# === CUSTOM ROTATING LOG HANDLER ===
class RotatingLogHandler(logging.Handler):
    """
    Custom log handler that rotates files using a1-z26 naming scheme
    and can switch files mid-operation if needed.
    """
    def __init__(self, log_dir, base_name, maxBytes=MAX_FILE_SIZE_BYTES, backupCount=676):
        super().__init__()
        self.log_dir = log_dir
        self.base_name = base_name
        self.maxBytes = maxBytes
        self.backupCount = backupCount
        self.current_file = None
        self.current_size = 0
        self.current_suffix = 'a1'
        
        # Start with first file - FIXED: use empty string instead of bytes
        self._rotate_if_needed('')

    def _get_next_suffix(self, current_suffix):
        """Get next suffix in a1-z26 sequence"""
        if not current_suffix:
            return 'a1'
        
        letter = current_suffix[0]
        number = int(current_suffix[1:])
        
        if number < 26:
            return f"{letter}{number + 1}"
        else:
            next_letter = chr(ord(letter) + 1)
            if next_letter <= 'z':
                return f"{next_letter}1"
            else:
                return None  # No more suffixes available

    def _get_file_path(self, suffix):
        return os.path.join(self.log_dir, f"{self.base_name}{suffix}.txt")

    def _rotate_if_needed(self, message):
        """Rotate to next file if current one would exceed size limit"""
        # FIXED: Handle both string and bytes for message size calculation
        if isinstance(message, bytes):
            message_size = len(message)
        else:
            message_size = len(message.encode('utf-8'))
        
        if self.current_file is None or (self.current_size + message_size) > self.maxBytes:
            if self.current_file:
                self.current_file.close()
            
            # Get next available suffix
            next_suffix = self._get_next_suffix(self.current_suffix)
            if next_suffix is None:
                # We've used all a1-z26, start overwriting from a1?
                # For safety, we'll just keep using the last file
                next_suffix = 'z26'
            
            self.current_suffix = next_suffix
            new_file_path = self._get_file_path(next_suffix)
            
            # Open new file
            self.current_file = open(new_file_path, 'a', encoding='utf-8')
            self.current_size = os.path.getsize(new_file_path) if os.path.exists(new_file_path) else 0

    def emit(self, record):
        try:
            message = self.format(record) + '\n'
            msg_size = len(message.encode('utf-8'))
            
            # Check if we need to rotate before writing
            self._rotate_if_needed(message)
            
            # Write the message
            if self.current_file:
                self.current_file.write(message)
                self.current_file.flush()
                self.current_size += msg_size
                
        except Exception as e:
            print(f"Logging error: {e}")

    def close(self):
        if self.current_file:
            self.current_file.close()
        super().close()

# === LOGGING SETUP ===
def setup_logging():
    """Set up daily logging with file rotation for large log files"""
    log_dir = os.path.join("Output", "Logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Base log filename without rotation
    log_basename = f"{datetime.date.today()}-dayz-log"
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Custom handler that rotates files when they approach the size limit
    rotating_handler = RotatingLogHandler(log_dir, log_basename, maxBytes=MAX_FILE_SIZE_BYTES, backupCount=676)
    rotating_handler.setLevel(logging.DEBUG)
    
    # Console handler to maintain normal terminal output - ONLY WARNINGS AND ERRORS
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)  # Only show warnings and errors
    
    # Formatter with timestamp
    formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
    rotating_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(rotating_handler)
    logger.addHandler(console_handler)
    
    return logger

# === FILE WRITING FUNCTIONS WITH SIZE LIMITS AND ROTATION ===
def write_creature_chunk(base_dir, base_filename, content):
    """
    Write complete creature chunks to files with a1-z26 rotation.
    Each file contains complete creature entries (from separator to separator).
    """
    # Generate the base filename pattern (without rotation suffix)
    name_part = base_filename.rsplit('.', 1)[0] if '.' in base_filename else base_filename
    
    # Find the next available file that can fit this chunk
    file_path = find_available_creature_file(base_dir, name_part, content)
    
    if not file_path:
        logger.error(f"No available file could fit chunk for {name_part}")
        return False
    
    try:
        # Write the complete chunk
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content + '\n\n')  # Double newline between creatures
        
        return True
        
    except IOError as e:
        logger.error(f"Error writing to {file_path}: {e}")
        return False

def find_available_creature_file(base_dir, name_part, content):
    """
    Find available file using a1-z26 rotation scheme.
    Returns the first file that can fit the content without splitting chunks.
    """
    content_size = len(content.encode('utf-8'))
    
    # Try existing files first
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        for number in range(1, 27):
            filename = f"{name_part}{letter}{number}.txt"
            file_path = os.path.join(base_dir, filename)
            
            if not os.path.exists(file_path):
                # New file - will definitely fit
                return file_path
            
            # Check if existing file has space
            current_size = os.path.getsize(file_path)
            if current_size + content_size <= MAX_FILE_SIZE_BYTES:
                return file_path
    
    # If we've exhausted a1-z26, we can't create more files for this base name today
    logger.error(f"No available files in a1-z26 range for {name_part}")
    return None

# === ENHANCED DUPLICATE CHECKING SYSTEM ===
def extract_attributes_from_content(content):
    """
    Extract the core attributes from creature content, ignoring creation order numbers
    """
    attributes = {}
    
    # Extract name
    name_match = re.search(r"Name:\s*(.+)", content)
    if name_match:
        attributes['name'] = name_match.group(1).strip()
    
    # Extract shape
    shape_match = re.search(r"Shape:\s*(.+)", content)
    if shape_match:
        attributes['shape'] = shape_match.group(1).strip()
    
    # Extract type
    type_match = re.search(r"Type:\s*(.+)", content)
    if type_match:
        attributes['type'] = type_match.group(1).strip()
    
    # Extract size
    size_match = re.search(r"Size:\s*(.+)", content)
    if size_match:
        attributes['size'] = size_match.group(1).strip()
    
    # Extract elements
    elements_match = re.search(r"Element\(s\):\s*(.+)", content)
    if elements_match:
        elements_str = elements_match.group(1).strip()
        # Convert to sorted tuple for consistent comparison
        attributes['elements'] = tuple(sorted([e.strip() for e in elements_str.split(',')]))
    
    # Extract specialized adaptation
    adaptation_match = re.search(r"Specialized Adaptation:\s*(.+)", content)
    if adaptation_match:
        attributes['adaptation'] = adaptation_match.group(1).strip()
    else:
        # Check if it's in the public format
        adaptation_match = re.search(r"Specialized Adaptation:\s*(.+)", content)
        if adaptation_match:
            attributes['adaptation'] = adaptation_match.group(1).strip()
        else:
            attributes['adaptation'] = "No Specialized Adaptation"
    
    return attributes

def calculate_similarity(attrs1, attrs2):
    """
    Calculate how many attributes match between two creatures
    """
    matching_attributes = 0
    total_attributes = 0
    
    for key in ['name', 'shape', 'type', 'size', 'elements', 'adaptation']:
        if key in attrs1 and key in attrs2:
            total_attributes += 1
            if attrs1[key] == attrs2[key]:
                matching_attributes += 1
    
    return matching_attributes, total_attributes

def is_duplicate_by_attributes(directory, new_attributes, num_elements):
    """
    Check if a creature is a duplicate based on attribute similarity
    Rules:
    - For 4 elements: consider duplicate if 2+ attributes match
    - For 5 elements: consider duplicate if 3+ attributes match  
    - Adjust threshold based on number of elements
    """
    if not os.path.exists(directory):
        return False
    
    # Determine threshold based on number of elements
    if num_elements <= 3:
        threshold = 2  # More strict for fewer elements
    elif num_elements == 4:
        threshold = 2  # 2 matches considered duplicate
    else:  # 5 or more elements
        threshold = 3  # 3 matches considered duplicate
    
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    
                    # Extract attributes from existing file (ignoring creation order)
                    existing_attributes = extract_attributes_from_content(file_content)
                    
                    # Calculate similarity
                    matching_attrs, total_attrs = calculate_similarity(existing_attributes, new_attributes)
                    
                    # Check if exceeds threshold
                    if matching_attrs >= threshold:
                        return True
                        
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
    
    return False

def is_content_duplicate(directory, content):
    """
    Updated duplicate check that uses attribute-based comparison
    """
    # Extract attributes from new content (ignoring creation order)
    new_attributes = extract_attributes_from_content(content)
    
    # Get number of elements for threshold calculation
    num_elements = len(new_attributes.get('elements', []))
    
    return is_duplicate_by_attributes(directory, new_attributes, num_elements)

def create_file_with_duplicate_check(artist_dir, public_dir, filename, content_artist, content_public, size):
    start_time = datetime.datetime.now()
    
    # Create size-specific subdirectories
    artist_size_dir = os.path.join(artist_dir, size)
    public_size_dir = os.path.join(public_dir, size)
    
    os.makedirs(artist_size_dir, exist_ok=True)
    os.makedirs(public_size_dir, exist_ok=True)

    # Extract base filename without extension for rotation scheme
    base_filename = filename.rsplit('.', 1)[0] if '.' in filename else filename
    
    # Extract number of elements for duplicate threshold
    elements_match = re.search(r"Element\(s\):\s*(.+)", content_artist)
    num_elements = 0
    if elements_match:
        elements_str = elements_match.group(1).strip()
        num_elements = len([e.strip() for e in elements_str.split(',')])
    
    # Use attribute-based duplicate checking
    if is_content_duplicate(artist_size_dir, content_artist):
        artist_success = True  # Consider skipping as success
    else:
        artist_success = write_creature_chunk(artist_size_dir, base_filename, content_artist)
    
    if is_content_duplicate(public_size_dir, content_public):
        public_success = True  # Consider skipping as success
    else:
        public_success = write_creature_chunk(public_size_dir, base_filename, content_public)
    
    return artist_success and public_success

# Initialize logging
logger = setup_logging()

# Initialize creature creation counter
creature_creation_counter = 0

# Initialize creature tally for current session
creature_tally = defaultdict(int)
size_tally = defaultdict(lambda: defaultdict(int))  # subcategory -> size -> count
size_stats = defaultdict(lambda: defaultdict(list))  # size -> stat -> list of values

# Log script start
logger.info("=== SCRIPT STARTED ===")

# Import skew configuration
try:
    from skew import SKEW_CONFIG
except ImportError:
    # Fallback configuration if skew_config.py doesn't exist
    SKEW_CONFIG = {
        'subcategory_skew': 1.0,
        'size_skew': 1.0,
        'size_preferences': {
            'Tiny': 1.0, 'Small': 1.0, 'Mid': 1.0, 
            'Large': 1.0, 'Giant': 1.0, 'Mega': 1.0, 'Super': 1.0
        },
        'category_preferences': {
            'Bird': 1.0, 'Amphibian': 1.0, 'Vertebrate': 1.0,
            'Reptile': 1.0, 'Fish': 1.0, 'Invertebrate': 1.0
        }
    }
    logger.warning("skew_config.py not found, using default uniform distribution")

rerunYesNo = ["yes", "no"]

directories = [
    "Creature_parts/BodyShapes/Amphibians",
    "Creature_parts/BodyShapes/Birds",
    "Creature_parts/BodyShapes/Fish",
    "Creature_parts/BodyShapes/Invertebrates",
    "Creature_parts/BodyShapes/Reptiles",
    "Creature_parts/BodyShapes/Vertebrates"
]

nameList1 = "Creature_parts/Genus.txt"
nameList2 = "Creature_parts/Epithet.txt"
nameList3 = "Creature_parts/Subspecies.txt"
nameList4 = "Creature_parts/Varietal.txt"
nameList5 = "Creature_parts/Behavioral.txt"

sizeList = ["Tiny", "Small", "Mid", "Large", "Giant", "Mega", "Super"]

typeList = ["Close", "Mid", "Range", "Long Range", "Ground", "Water", "Lava/Magma", "Sky", "Underground", "Day", "Night", "Pack", "Group", "Horde"]
typePerc = [7.14] * 14
interferingTypes = {
    "Close": ["Mid", "Range", "Long Range"],
    "Mid": ["Close", "Range", "Long Range"],
    "Range": ["Close", "Mid", "Long Range"],
    "Long Range": ["Close", "Mid", "Range"],
    "Sky": ["Underground"],
    "Underground": ["Sky"],
    "Day": ["Night"],
    "Night": ["Day"],
    "Group": ["Pack", "Horde"],
    "Pack": ["Group", "Horde"],
    "Horde": ["Group", "Pack"],
    "Water": ["Lava/Magma"],
    "Lava/Magma": ["Water"]
}
bioList = "Creature_parts/BodyShapes/Specialized_adaptations/Bioluminescent.txt"
extList = "Creature_parts/BodyShapes/Specialized_adaptations/Extreme_Camouflage.txt"

basicElementList = ["Physical", "Fire", "Earth", "Gold", "Water", "Wood"]
belPerc = [16.6] * 6
variantElementList = ["Strength", "Lightning", "Crystal", "Sharpness", "Ice", "Wind"]
velPerc = [16.6] * 6
higherElementList = ["Yin", "Yang"]
helPerc = [50, 50]
primordialElementList = ["Time", "Space", "Chaos"]
pelPerc = [33.3] * 3
elementList = [basicElementList, variantElementList, higherElementList, primordialElementList]
elPerc = [70, 20, 7.5, 2.5]
promoting = {"Fire": "Earth", "Earth": "Gold", "Gold": "Water", "Water": "Wood", "Wood": "Fire"}
restraining = {"Fire": "Earth", "Earth": "Gold", "Gold": "Water", "Water": "Wood", "Wood": "Fire"}
derivedFrom = {
    "Strength": "Physical",
    "Lightning": "Fire",
    "Crystal": "Earth",
    "Sharpness": "Gold",
    "Ice": "Water",
    "Wind": "Wood"
}
yinElements = {"Ice", "Water", "Earth", "Wood", "Wind"}
yangElements = {"Gold", "Sharpness", "Crystal", "Lightning", "Fire"}
illegalCombinations = {"Chaos": {"Time", "Space"}}

CATEGORY_MAP = {
    "Amphibian": {
        "subcategories": {
            "Aquatic Paedomorphic": "AP",
            "Arboreal Frog": "AF",
            "Fossorial Amphibian": "FA"
        },
        "base_path": "Amphibians"
    },
    "Bird": {
        "subcategories": {
            "Aerial Song Bird": "ASB",
            "Aquatic Swimming Bird": "AQSB",
            "Flightless Heavy Bodied Bird": "FHBB",
            "Raptorial": "R",
            "Wading Long Legged Bird": "WLLB"
        },
        "base_path": "Birds"
    },
    "Fish": {
        "subcategories": {
            "Anguilliform": "AF",
            "Benthic": "B",
            "Compressiform": "CF",
            "Fusiform": "FF",
            "Globiform": "GF"
        },
        "base_path": "Fish"
    },
    "Invertebrate": {
        "subcategories": {
            "Arthropod": "A",
            "Gelatinous": "G",
            "Mollusk": "M",
            "Radial Symmetry": "RS",
            "Elongate": "ER"
        },
        "base_path": "Invertebrates"
    },
    "Reptile": {
        "subcategories": {
            "Arboreal Reptile": "AR",
            "Armoured Scuted Reptile": "ASR",
            "Fossorial Reptile": "FR",
            "Serpent": "S",
            "Semi-Aquatic Reptile": "SAR"
        },
        "base_path": "Reptiles"
    },
    "Vertebrate": {
        "subcategories": {
            "Arboreal Quadrupedal": "AQ",
            "Cursorial Quadrupedal": "CQ",
            "Fossorial Quadrupedal": "FQ",
            "Graviportal Quadrupedal": "GQ",
            "Semi-Aquatic Quadrupedal": "SAQ"
        },
        "base_path": "Vertebrates"
    }
}

# === SKEWING FUNCTIONS ===
def apply_skew(choices, base_weights, skew_factor):
    """Apply power transformation to skew distribution"""
    if not choices or len(choices) != len(base_weights):
        return base_weights
    
    skewed_weights = []
    for weight in base_weights:
        # Apply power transformation - higher skew_factor creates more extreme differences
        skewed_weight = weight ** skew_factor
        skewed_weights.append(skewed_weight)
    
    return skewed_weights

def get_skewed_size():
    """Get size with skewed distribution based on preferences"""
    sizes = sizeList.copy()
    
    # Apply size preferences
    weights = [SKEW_CONFIG['size_preferences'].get(size, 1.0) for size in sizes]
    
    # Apply additional skew
    final_weights = apply_skew(sizes, weights, SKEW_CONFIG['size_skew'])
    
    return random.choices(sizes, weights=final_weights, k=1)[0]

def get_skewed_category_directory():
    """Get directory with category-based skewing"""
    # Create weights based on category preferences
    weights = []
    for directory in directories:
        # Extract category from directory path
        category = directory.split('/')[-1]
        if category.endswith('s'):
            category = category[:-1]  # Remove plural 's'
        
        weight = SKEW_CONFIG['category_preferences'].get(category, 1.0)
        weights.append(weight)
    
    # Apply additional skew
    final_weights = apply_skew(directories, weights, SKEW_CONFIG['subcategory_skew'])
    
    return random.choices(directories, weights=final_weights, k=1)[0]

class ConflictFreeTypeSelector:
    def __init__(self):
        self.available = typeList.copy()
        self.selected = []
    
    def choose_type(self):
        if not self.available:
            return None
        
        chosen = random.choice(self.available)
        self.selected.append(chosen)
        
        conflicts = interferingTypes.get(chosen, [])
        self.available = [t for t in self.available 
                          if t not in conflicts and t != chosen]
        
        return chosen
    
    def reset(self):
        self.available = typeList.copy()
        self.selected = []

def run_simulation():
    selector = ConflictFreeTypeSelector()
    selections = []
    
    while selector.available:
        chosen = selector.choose_type()
        if chosen is None:
            break
        selections.append(chosen)
    return selections

class ElementListManager:
    def __init__(self, items, initial_weights, list_type):
        self.items = items.copy()
        self.initial_weights = [w for w in initial_weights]
        self.available = self.items.copy()
        self.weights = self.initial_weights.copy()
        self.list_type = list_type

    def choose_element(self):
        if not self.available:
            return None
        chosen = random.choices(self.available, weights=self.weights, k=1)[0]
        self._remove_element(chosen)
        return chosen

    def _remove_element(self, element):
        idx = self.available.index(element)
        self.available.pop(idx)
        self.weights.pop(idx)

    def reset(self):
        self.available = self.items.copy()
        self.weights = self.initial_weights.copy()

def update_weights_based_on_rules(chosen_element, manager):
    if chosen_element in promoting:
        promoted = promoting[chosen_element]
        if promoted in manager.available:
            idx = manager.available.index(promoted)
            manager.weights[idx] *= 1.1

    if chosen_element in restraining:
        restrained = restraining[chosen_element]
        if restrained in manager.available:
            idx = manager.available.index(restrained)
            manager.weights[idx] *= 0.9
    
    if chosen_element in derivedFrom:
        derived = derivedFrom[chosen_element]
        if derived in manager.available:
            idx = manager.available.index(derived)
            manager.weights[idx] *= 1.2

    if chosen_element in yinElements:
        for elem in manager.available:
            if elem in yangElements:
                idx = manager.available.index(elem)
                manager.weights[idx] *= 0.8
    elif chosen_element in yangElements:
        for elem in manager.available:
            if elem in yinElements:
                idx = manager.available.index(elem)
                manager.weights[idx] *= 0.8

def run_selection_process(random_size, selected_elements):
    managers = {
        "basic": ElementListManager(basicElementList, belPerc, "basic"),
        "variant": ElementListManager(variantElementList, velPerc, "variant"),
        "higher": ElementListManager(higherElementList, helPerc, "higher"),
        "primordial": ElementListManager(primordialElementList, pelPerc, "primordial")
    }

    multipleElements = False
    elements = 1
    while not multipleElements and elements < 4:
        valid_lists = elementList.copy()
        valid_weights = elPerc.copy()
        if random_size != "Super":
            if primordialElementList in valid_lists:
                valid_lists.remove(primordialElementList)
                valid_weights.pop(-1)

        chosen_list = random.choices(valid_lists, weights=valid_weights, k=1)[0]
        list_name = ["basic", "variant", "higher", "primordial"][elementList.index(chosen_list)]

        manager = managers[list_name]
        elem = manager.choose_element()
        if elem is None:
            continue

        if elem == "Chaos" and any(e in selected_elements for e in illegalCombinations["Chaos"]):
            selected_elements.clear()
            return run_selection_process(random_size, selected_elements)

        selected_elements.append(elem)

        for mgr in managers.values():
            update_weights_based_on_rules(elem, mgr)

        if list_name == "basic":
            rerun_weights = [60, 40]
        elif list_name == "variant":
            rerun_weights = [25, 75]
        elif list_name == "higher":
            rerun_weights = [10, 90]
        elif list_name == "primordial":
            rerun_weights = [5, 95]

        rerun = random.choices(rerunYesNo, weights=rerun_weights, k=1)[0]

        if rerun == "no":
            multipleElements = True
        else:
            elements += 1

    return selected_elements

def calculate_atk(base_atk, selected_elements):
    element_multipliers = {
        "Fire": 1.100,
        "Lightning": 1.250,
        "Sharpness": 1.300,
        "Physical": 1.050,
        "Strength": 1.075,
        "Crystal": 1.400,
        "Ice": 1.27,
        "Time": 2.500,
        "Space": 2.300,
        "Chaos": 2.100
    }
    
    multipliers = [element_multipliers.get(element, 1.0) for element in selected_elements]
    multipliers.sort(reverse=True)
    
    result = base_atk
    for multiplier in multipliers:
        result *= multiplier
    
    return round(result, 1)

def calculate_def(base_def, selected_elements):
    element_multipliers = {
        "Physical": 1.050,
        "Gold": 1.200,
        "Wind": 1.350,
        "Crystal": 1.400,
        "Earth": 1.200,
        "Wood": 1.300,
        "Time": 2.500,
        "Space": 2.300,
        "Chaos": 2.100
    }
    
    multipliers = [element_multipliers.get(element, 1.0) for element in selected_elements]
    multipliers.sort(reverse=True)
    
    result = base_def
    for multiplier in multipliers:
        result *= multiplier
    
    return round(result, 1)

def calculate_agi(base_agi, selected_elements):
    element_multipliers = {
        "Lightning": 1.250,
        "Wind": 1.350,
        "Water": 1.250,
        "Chaos": 2.100
    }
    
    multipliers = [element_multipliers.get(element, 1.0) for element in selected_elements]
    multipliers.sort(reverse=True)
    
    result = base_agi
    for multiplier in multipliers:
        result *= multiplier
    
    return round(result, 1)

def calculate_int(base_int, selected_elements):
    element_multipliers = {
        "Fire": 1.100,
        "Yang": 1.500,
        "Gold": 1.200,
        "Yin": 1.500,
        "Water": 1.25,
        "Space": 2.300,
        "Ice": 1.270
    }
    
    multipliers = [element_multipliers.get(element, 1.0) for element in selected_elements]
    multipliers.sort(reverse=True)
    
    result = base_int
    for multiplier in multipliers:
        result *= multiplier
    
    return round(result, 1)

def calculate_wis(base_wis, selected_elements):
    element_multipliers = {
        "Yang": 1.500,
        "Yin": 1.500,
        "Wood": 1.300,
        "Time": 2.500
    }
    
    multipliers = [element_multipliers.get(element, 1.0) for element in selected_elements]
    multipliers.sort(reverse=True)
    
    result = base_wis
    for multiplier in multipliers:
        result *= multiplier
    
    return round(result, 1)

def get_random_line(file_path):
    line = None
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, current_line in enumerate(f):
            if random.randint(0, i) == 0:
                line = current_line.strip()
    return line

def get_random_name(namelist):
    name = None
    with open(namelist, 'r', encoding='utf-8') as f:
        for i, current_name in enumerate(f):
            if random.randint(0, i) == 0:
                name = current_name.strip()
    return name

def get_random_spec(speclist):
    spec = None
    with open(speclist, 'r', encoding='utf-8') as f:
        for i, current_spec in enumerate(f):
            if random.randint(0, i) == 0:
                spec = current_spec.strip()
    return spec

def save_current_tally():
    """Save the current session tally to cumulative files"""
    # Save subcategory counts
    subcategory_file = os.path.join("Output", "Logs", "cumulative_subcategories.json")
    cumulative_subcategories = defaultdict(int)
    
    if os.path.exists(subcategory_file):
        try:
            with open(subcategory_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                for subcategory, count in existing_data.items():
                    cumulative_subcategories[subcategory] = count
        except Exception as e:
            logger.error(f"Error loading cumulative subcategories: {e}")
    
    # Add current session to cumulative subcategories
    for subcategory, count in creature_tally.items():
        cumulative_subcategories[subcategory] += count
    
    # Save updated cumulative subcategories
    try:
        with open(subcategory_file, 'w', encoding='utf-8') as f:
            json.dump(dict(cumulative_subcategories), f, indent=2)
    except Exception as e:
        logger.error(f"Error saving cumulative subcategories: {e}")
    
    # Save size breakdown
    size_file = os.path.join("Output", "Logs", "cumulative_sizes.json")
    cumulative_sizes = defaultdict(lambda: defaultdict(int))
    
    if os.path.exists(size_file):
        try:
            with open(size_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                for subcategory, sizes in existing_data.items():
                    for size, count in sizes.items():
                        cumulative_sizes[subcategory][size] = count
        except Exception as e:
            logger.error(f"Error loading cumulative sizes: {e}")
    
    # Add current session to cumulative sizes
    for subcategory, sizes in size_tally.items():
        for size, count in sizes.items():
            cumulative_sizes[subcategory][size] += count
    
    # Save updated cumulative sizes
    try:
        # Convert defaultdict to regular dict for JSON serialization
        serializable_sizes = {}
        for subcategory, sizes in cumulative_sizes.items():
            serializable_sizes[subcategory] = dict(sizes)
        with open(size_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_sizes, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving cumulative sizes: {e}")
    
    # Save size stats
    stats_file = os.path.join("Output", "Logs", "cumulative_stats.json")
    cumulative_stats = defaultdict(lambda: defaultdict(list))
    
    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                for size, stats in existing_data.items():
                    for stat, values in stats.items():
                        cumulative_stats[size][stat] = values
        except Exception as e:
            logger.error(f"Error loading cumulative stats: {e}")
    
    # Add current session to cumulative stats
    for size, stats in size_stats.items():
        for stat, values in stats.items():
            cumulative_stats[size][stat].extend(values)
    
    # Save updated cumulative stats
    try:
        serializable_stats = {}
        for size, stats in cumulative_stats.items():
            serializable_stats[size] = dict(stats)
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_stats, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving cumulative stats: {e}")
    
    return cumulative_subcategories, cumulative_sizes, cumulative_stats

def load_cumulative_data():
    """Load all cumulative data from files"""
    subcategory_file = os.path.join("Output", "Logs", "cumulative_subcategories.json")
    size_file = os.path.join("Output", "Logs", "cumulative_sizes.json")
    stats_file = os.path.join("Output", "Logs", "cumulative_stats.json")
    
    cumulative_subcategories = defaultdict(int)
    cumulative_sizes = defaultdict(lambda: defaultdict(int))
    cumulative_stats = defaultdict(lambda: defaultdict(list))
    
    # Load subcategories
    if os.path.exists(subcategory_file):
        try:
            with open(subcategory_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                for subcategory, count in existing_data.items():
                    cumulative_subcategories[subcategory] = count
        except Exception as e:
            logger.error(f"Error loading cumulative subcategories: {e}")
    
    # Load sizes
    if os.path.exists(size_file):
        try:
            with open(size_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                for subcategory, sizes in existing_data.items():
                    for size, count in sizes.items():
                        cumulative_sizes[subcategory][size] = count
        except Exception as e:
            logger.error(f"Error loading cumulative sizes: {e}")
    
    # Load stats
    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                for size, stats in existing_data.items():
                    for stat, values in stats.items():
                        cumulative_stats[size][stat] = values
        except Exception as e:
            logger.error(f"Error loading cumulative stats: {e}")
    
    return cumulative_subcategories, cumulative_sizes, cumulative_stats

def calculate_averages(stats_data):
    """Calculate average stats from lists of values"""
    averages = {}
    for size, stats in stats_data.items():
        averages[size] = {}
        for stat, values in stats.items():
            if values:
                averages[size][stat] = sum(values) / len(values)
            else:
                averages[size][stat] = 0
    return averages

def log_creature_tally():
    """Log the current session and cumulative tallies with size breakdown and averages"""
    # Save current session and get updated cumulative data
    cumulative_subcategories, cumulative_sizes, cumulative_stats = save_current_tally()
    
    logger.info("=== CREATURE CREATION TALLY ===")
    
    # Current session tally
    if not creature_tally:
        logger.info("No creatures were created in this session.")
    else:
        logger.info("THIS SESSION:")
        total_this_session = sum(creature_tally.values())
        sorted_session = sorted(creature_tally.items(), key=lambda x: x[1], reverse=True)
        
        for subcategory, count in sorted_session:
            percentage = (count / total_this_session) * 100
            logger.info(f"  {subcategory}: {count} creatures ({percentage:.1f}%)")
            
            # Log size breakdown for this subcategory
            if subcategory in size_tally:
                size_breakdown = []
                for size in sizeList:
                    if size in size_tally[subcategory] and size_tally[subcategory][size] > 0:
                        size_breakdown.append(f"{size}: {size_tally[subcategory][size]}")
                if size_breakdown:
                    logger.info(f"    Sizes: {', '.join(size_breakdown)}")
        
        logger.info(f"TOTAL THIS SESSION: {total_this_session}")
        logger.info("")
    
    # Cumulative tally
    logger.info("CUMULATIVE TOTALS (ALL TIME):")
    if not cumulative_subcategories:
        logger.info("  No cumulative data available.")
    else:
        total_all_time = sum(cumulative_subcategories.values())
        sorted_cumulative = sorted(cumulative_subcategories.items(), key=lambda x: x[1], reverse=True)
        
        for subcategory, count in sorted_cumulative:
            percentage = (count / total_all_time) * 100
            logger.info(f"  {subcategory}: {count} creatures ({percentage:.1f}%)")
            
            # Log cumulative size breakdown for this subcategory
            if subcategory in cumulative_sizes:
                size_breakdown = []
                for size in sizeList:
                    if size in cumulative_sizes[subcategory] and cumulative_sizes[subcategory][size] > 0:
                        size_count = cumulative_sizes[subcategory][size]
                        size_percentage = (size_count / count) * 100
                        size_breakdown.append(f"{size}: {size_count} ({size_percentage:.1f}%)")
                if size_breakdown:
                    logger.info(f"    Sizes: {', '.join(size_breakdown)}")
        
        logger.info(f"GRAND TOTAL ALL CREATURES: {total_all_time}")
        logger.info("")
    
    # Average stats per size
    logger.info("AVERAGE STATS PER SIZE (CUMULATIVE):")
    cumulative_averages = calculate_averages(cumulative_stats)
    
    for size in sizeList:
        if size in cumulative_averages and cumulative_averages[size]:
            logger.info(f"  {size}:")
            stats = cumulative_averages[size]
            if 'ATK' in stats:
                logger.info(f"    ATK: {stats['ATK']:.1f}, DEF: {stats['DEF']:.1f}, AGI: {stats['AGI']:.1f}, "
                           f"INT: {stats['INT']:.1f}, WIS: {stats['WIS']:.1f}")
    
    logger.info("=== END TALLY ===")
    
    return cumulative_subcategories, cumulative_sizes, cumulative_stats

# Function to handle the global counter
def get_next_creation_number():
    global creature_creation_counter
    creature_creation_counter += 1
    return creature_creation_counter

if __name__ == "__main__":
    try:
        # Display welcome message
        print("🧬 Creature Generator")
        print("=" * 50)
        
        # Log the question and capture user input
        amountOfCreatures = int(input("How many creatures do you wanna make? "))
        print(f"\n🎯 Generating {amountOfCreatures} creatures per category...")
        
        totalCreatedCreatures = 0
        total_target = amountOfCreatures * len(directories)

        # Initialize ETA tracker
        eta_tracker = CreatureETA(total_target)
        
        max_attempts_per_creature = 10

        print(f"📁 Processing {len(directories)} categories...")
        print(f"🎯 Total target: {total_target:,} creatures")
        print("\nStarting generation...\n")
        
        # Display initial progress
        eta_tracker.display_progress(force_display=True)

        while totalCreatedCreatures < total_target:
            # Use skewed category selection instead of simple rotation
            directory = get_skewed_category_directory()
            
            attempts = 0
            success = False
            while attempts < max_attempts_per_creature and not success:
                attempts += 1

                files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
                if not files:
                    break

                random_file = random.choice(files)
                full_path = os.path.join(directory, random_file)
                random_line = get_random_line(full_path)

                random_name_amount = random.randint(1, 5)
                final_name = []
                for i in range(1, random_name_amount + 1):
                    name_list = globals()[f"nameList{i}"]
                    final_name.append(get_random_name(name_list))

                # Use skewed size selection instead of random.choice
                random_size = get_skewed_size()

                selection = run_simulation()

                chanceForSpecializedAdaptation = random.randint(1, 3)
                specialized_artist = "No Specialized Adaptation"
                specialized_public = "no"
                random_bio = None
                random_ext = None
                if chanceForSpecializedAdaptation == 2:
                    random_bio = get_random_spec(bioList)
                    specialized_artist = "Bioluminescent " + (random_bio if random_bio else "")
                    specialized_public_message = "Bioluminescent"
                elif chanceForSpecializedAdaptation == 3:
                    random_ext = get_random_spec(extList)
                    specialized_artist = "Extreme Camouflage " + (random_ext if random_ext else "")
                    specialized_public_message = "Extreme Camouflage"
                else:
                    specialized_public_message = ""

                if specialized_public == "no":
                    specialized_public_message = ""

                selected_elements = []
                selected_elements = run_selection_process(random_size, selected_elements)

                if random_size == "Tiny":
                    min_val, max_val = 5, 8
                elif random_size == "Small":
                    min_val, max_val = 7, 10
                elif random_size == "Mid":
                    min_val, max_val = 11, 15
                elif random_size == "Large":
                    min_val, max_val = 17, 22
                elif random_size == "Giant":
                    min_val, max_val = 25, 30
                elif random_size == "Mega":
                    min_val, max_val = 37, 50
                elif random_size == "Super":
                    min_val, max_val = 66, 100

                stat_atk = random.randint(min_val, max_val)
                stat_def = random.randint(min_val, max_val)
                stat_agi = random.randint(min_val, max_val)
                stat_int = random.randint(min_val, max_val)
                stat_wis = random.randint(min_val, max_val)

                calculated_atk = calculate_atk(stat_atk, selected_elements)
                calculated_def = calculate_def(stat_def, selected_elements)
                calculated_agi = calculate_agi(stat_agi, selected_elements)
                calculated_int = calculate_int(stat_int, selected_elements)
                calculated_wis = calculate_wis(stat_wis, selected_elements)

                # Store stats for averaging
                size_stats[random_size]['ATK'].append(calculated_atk)
                size_stats[random_size]['DEF'].append(calculated_def)
                size_stats[random_size]['AGI'].append(calculated_agi)
                size_stats[random_size]['INT'].append(calculated_int)
                size_stats[random_size]['WIS'].append(calculated_wis)

                if calculated_atk != stat_atk:
                    atk_message = f"ATK: {calculated_atk:.1f} because of elemental bonuses, base ATK: {stat_atk:.1f}"
                else:
                    atk_message = f"ATK: {stat_atk:.1f}"

                if calculated_def != stat_def:
                    def_message = f"DEF: {calculated_def:.1f} because of elemental bonuses, base DEF: {stat_def:.1f}"
                else:
                    def_message = f"DEF: {stat_def:.1f}"

                if calculated_agi != stat_agi:
                    agi_message = f"AGI: {calculated_agi:.1f} because of elemental bonuses, base AGI: {stat_agi:.1f}"
                else:
                    agi_message = f"AGI: {stat_agi:.1f}"

                if calculated_int != stat_int:
                    int_message = f"INT: {calculated_int:.1f} because of elemental bonuses, base INT: {stat_int:.1f}"
                else:
                    int_message = f"INT: {stat_int:.1f}"

                if calculated_wis != stat_wis:
                    wis_message = f"WIS: {calculated_wis:.1f} because of elemental bonuses, base WIS: {stat_wis:.1f}"
                else:
                    wis_message = f"WIS: {stat_wis:.1f}"

                def calculate_hp():
                    return round((calculated_def + (calculated_atk * 0.1)) * 10, 1)

                def calculate_mana():
                    return round((calculated_int + (calculated_wis * 0.5)) * 5, 1)

                summary_output_artist = f"{atk_message}\n{def_message}\n{agi_message}\n{int_message}\n{wis_message}\nHP: {calculate_hp()} MANA: {calculate_mana()}"
                
                summary_output_public = f"ATK: {calculated_atk}\nDEF: {calculated_def}\nAGI: {calculated_agi}\nINT: {calculated_int}\nWIS: {calculated_wis}\nHP: {calculate_hp()} MANA: {calculate_mana()}"

                target_filename = random_file
                pattern = re.compile(rf"^.*?\b{re.escape(target_filename)}\b.*?=\s*(.*?)\s*(#|$)", re.IGNORECASE)

                extracted_texts = [None] * 3
                for i in range(3):
                    search_file = f"Required_Text{i}.txt"
                    try:
                        with open(search_file, "r") as f:
                            for line in f:
                                match = pattern.search(line)
                                if match:
                                    extracted_texts[i] = match.group(1).strip()
                                    break
                    except FileNotFoundError:
                        pass
                    except Exception:
                        pass

                if all(extracted_texts):
                    extracted_text0, extracted_text1, extracted_text2 = extracted_texts
                else:
                    # Placeholder handling if no match
                    category_dir = os.path.basename(directory)
                    map_key = category_dir[:-1] if category_dir.endswith('s') and category_dir != "Fish" else category_dir
                    category_config = CATEGORY_MAP.get(map_key)
                    if category_config is None:
                        continue

                    extracted_text1 = map_key
                    extracted_text0 = random.choice(list(category_config["subcategories"].keys()))
                    extracted_text2 = random_line if random_line else "Default description"

                category_config = CATEGORY_MAP.get(extracted_text1)
                if not category_config:
                    continue

                subcat_abbr = category_config["subcategories"].get(extracted_text0)
                if not subcat_abbr:
                    continue

                # Update creature tally and size tracking
                creature_tally[extracted_text0] += 1
                size_tally[extracted_text0][random_size] += 1

                base_path = category_config["base_path"]
                base_dir = base_path
                artist_dir = os.path.join("Output", "Artist", base_path)
                public_dir = os.path.join("Output", "Public", base_path)

                date_str = datetime.datetime.now().strftime("%Y%m%d")
                filename = f"{subcat_abbr}_{date_str}.txt"

                # Calculate the creation order number for this creature
                creation_order = get_next_creation_number()

                # Create separators with creation order number
                separator_artist_start = "🖌️"
                separator_artist_end = "❎"
                # Insert creation order in the middle of the upper separator
                separator_artist_upper_left = "x-" * 20  # 40 characters
                separator_artist_upper_right = "-x" * 20  # 40 characters
                separator_artist_upper = f"{separator_artist_upper_left} #{creation_order:04d} {separator_artist_upper_right}"

                separator_artist_lower = "-x" * 48

                # For public separator
                separator_public_upper_left = "-x" * 20  # 40 characters  
                separator_public_upper_right = "x-" * 20  # 40 characters
                separator_public_upper = f"{separator_public_upper_left} #{creation_order:04d} {separator_public_upper_right}"

                separator_public_lower = "x-" * 49

                content_artist = (
                    f"{separator_artist_start}{separator_artist_upper}{separator_artist_end}\n"
                    f"Name: {' '.join(final_name)}\n"
                    f"Shape: {extracted_text1}, {extracted_text0}, {extracted_text2}\n"
                    f"Type: {', '.join(selection)}\n"
                    f"Size: {random_size}\n"
                    f"Element(s): {', '.join(selected_elements)}\n"
                    f"Specialized Adaptation: {specialized_artist}\n"
                    "Stats:\n"
                    f"{summary_output_artist}\n"
                    f"{separator_artist_start}{separator_artist_lower}{separator_artist_end}"
                )

                spec_line = f"Specialized Adaptation: {specialized_public_message}\n" if specialized_public_message else ''

                content_public = (
                    f"{separator_public_upper}\n"
                    f"Name: {' '.join(final_name)}\n"
                    f"Shape: {extracted_text1}\n"
                    f"Type: {', '.join(selection)}\n"
                    f"Size: {random_size}\n"
                    f"Element(s): {', '.join(selected_elements)}\n"
                    f"{spec_line}"
                    "Stats:\n"
                    f"{summary_output_public}\n"
                    f"{separator_public_lower}"
                )

                # Use the new file writing system with size limits and rotation
                success = create_file_with_duplicate_check(artist_dir, public_dir, filename, content_artist, content_public, random_size)

                totalCreatedCreatures += 1
                success = True
                
                # Update ETA display
                eta_tracker.creatures_completed = totalCreatedCreatures
                eta_tracker.display_progress()

            if not success:
                totalCreatedCreatures += amountOfCreatures

        # Final completion message
        total_time = time.time() - eta_tracker.start_time
        accuracy_analysis = eta_tracker.finalize(total_time)
        
        # Clear the progress line and show completion
        print('\r' + ' ' * 100, end='')
        print(f'\r✅ Generation completed!')
        print(f"📊 Total creatures: {totalCreatedCreatures:,}")
        print(f"⏱️  Total time: {str(timedelta(seconds=int(total_time)))}")
        print(f"🏃 Average rate: {totalCreatedCreatures/total_time*3600:,.0f} creatures/hour")
        
        # Log the final creature tally before completion
        log_creature_tally()
        
        logger.info("=== SCRIPT COMPLETED SUCCESSFULLY ===")

    except Exception as e:
        logger.error(f"Script failed with error: {e}")
        # Log whatever tally we have even if script failed
        log_creature_tally()
        logger.info("=== SCRIPT TERMINATED WITH ERRORS ===")