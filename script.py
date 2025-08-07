import os
import re
import random
import datetime

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
            print("Illegal combination! Resetting...")
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

def is_content_duplicate(directory, content):
    if not os.path.exists(directory):
        return False
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    if content in file_content:
                        return True
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    return False

def create_file_with_duplicate_check(artist_dir, public_dir, filename, content_artist, content_public):
    os.makedirs(artist_dir, exist_ok=True)
    os.makedirs(public_dir, exist_ok=True)

    artist_path = os.path.join(artist_dir, filename)
    if not is_content_duplicate(artist_dir, content_artist):
        with open(artist_path, 'a', encoding='utf-8') as f:
            f.write(content_artist + '\n')
        print(f"Appended to artist file: {artist_path}")
    else:
        print(f"Duplicate artist content found for {filename}, skipping")

    public_path = os.path.join(public_dir, filename)
    if not is_content_duplicate(public_dir, content_public):
        with open(public_path, 'a', encoding='utf-8') as f:
            f.write(content_public + '\n')
        print(f"Appended to public file: {public_path}")
    else:
        print(f"Duplicate public content found for {filename}, skipping")

if __name__ == "__main__":
    amountOfCreatures = int(input("How many creatures do you wanna make? "))
    totalCreatedCreatures = 0
    total_target = amountOfCreatures * len(directories)

    max_attempts_per_creature = 10

    while totalCreatedCreatures < total_target:
        category_index = totalCreatedCreatures // amountOfCreatures
        if category_index >= len(directories):
            print("Exceeded directories, stopping.")
            break
        directory = directories[category_index]

        attempts = 0
        success = False
        while attempts < max_attempts_per_creature and not success:
            attempts += 1

            files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
            if not files:
                print(f"No files in {directory}, skipping category.")
                break

            random_file = random.choice(files)
            full_path = os.path.join(directory, random_file)
            random_line = get_random_line(full_path)
            print(f"Random file: {full_path}")
            print(f"Random line: {random_line}")

            random_name_amount = random.randint(1, 5)
            final_name = []
            for i in range(1, random_name_amount + 1):
                name_list = globals()[f"nameList{i}"]
                final_name.append(get_random_name(name_list))
            print(final_name)

            random_size = random.choice(sizeList)
            print(random_size)

            selection = run_simulation()
            print(f"Final Selection: {selection}")

            chanceForSpecializedAdaptation = random.randint(1, 3)
            specialized_artist = "No Specialized Adaptation"
            specialized_public = "no"
            random_bio = None
            random_ext = None
            if chanceForSpecializedAdaptation == 2:
                random_bio = get_random_spec(bioList)
                print("Bioluminescent " + (random_bio if random_bio else ""))
                specialized_artist = "Bioluminescent " + (random_bio if random_bio else "")
                specialized_public_message = "Bioluminescent"
            elif chanceForSpecializedAdaptation == 3:
                random_ext = get_random_spec(extList)
                print("Extreme Camouflage " + (random_ext if random_ext else ""))
                specialized_artist = "Extreme Camouflage " + (random_ext if random_ext else "")
                specialized_public_message = "Extreme Camouflage"
            else:
                print("No Specialized Adaptation")
            
            if specialized_public == "no":
                specialized_public_message = ""

            selected_elements = []
            selected_elements = run_selection_process(random_size, selected_elements)
            print(f"Selected elements: {selected_elements}")

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
            print(f"Stats:\n{summary_output_artist}")
            
            summary_output_public = f"ATK: {calculated_atk}\nDEF: {calculated_def}\nAGI: {calculated_agi}\nINT: {calculated_int}\nWIS: {calculated_wis}\nHP: {calculate_hp()} MANA: {calculate_mana()}"
            print(f"Stats:\n{summary_output_public}")

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
                                print(f"MATCH FOUND in {search_file}: '{extracted_texts[i]}'")
                                break
                except FileNotFoundError:
                    print(f"Error: File '{search_file}' not found.")
                except Exception as e:
                    print(f"Error processing {search_file}: {e}")

            if all(extracted_texts):
                extracted_text0, extracted_text1, extracted_text2 = extracted_texts
            else:
                # Placeholder handling if no match
                category_dir = os.path.basename(directory)
                map_key = category_dir[:-1] if category_dir.endswith('s') and category_dir != "Fish" else category_dir
                category_config = CATEGORY_MAP.get(map_key)
                if category_config is None:
                    print(f"Invalid map key derived: {map_key}, skipping.")
                    continue

                extracted_text1 = map_key
                extracted_text0 = random.choice(list(category_config["subcategories"].keys()))
                extracted_text2 = random_line if random_line else "Default description"

            print(f"Using derived: Shape: {extracted_text1}, {extracted_text0}, {extracted_text2}")

            category_config = CATEGORY_MAP.get(extracted_text1)
            if not category_config:
                print(f"Invalid category: {extracted_text1}, skipping.")
                continue

            subcat_abbr = category_config["subcategories"].get(extracted_text0)
            if not subcat_abbr:
                print(f"Invalid subcategory: {extracted_text0}, skipping.")
                continue

            base_path = category_config["base_path"]
            base_dir = base_path
            artist_dir = os.path.join("Output", "Artist", base_path)
            public_dir = os.path.join("Output", "Public", base_path)

            date_str = datetime.datetime.now().strftime("%Y%m%d")
            filename = f"{subcat_abbr}_{date_str}.txt"

            separator_artist_start = "🖌️"
            separator_artist_end = "❎"
            separator_artist_upper = "x-" * 48
            separator_artist_lower = "-x" * 48
            separator_public_upper = "-x" * 49
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

            create_file_with_duplicate_check(artist_dir, public_dir, filename, content_artist, content_public)

            totalCreatedCreatures += 1
            success = True
            print(f"Total creatures created: {totalCreatedCreatures}/{total_target}")

        if not success:
            print(f"Max attempts reached for category {directory}, skipping to next.")
            totalCreatedCreatures += amountOfCreatures
        import os
    os.makedirs(artist_dir, exist_ok=True)
    os.makedirs(public_dir, exist_ok=True)

    if not is_content_duplicate(artist_dir, content_artist):
        artist_path = os.path.join(artist_dir, filename)
        with open(artist_path, 'a', encoding='utf-8') as f:
            f.write(content_artist)
        print(f"Appended to artist file: {artist_path}")
    else:
        print(f"Duplicate artist content found for {filename}, skipping")

    if not is_content_duplicate(public_dir, content_public):
        public_path = os.path.join(public_dir, filename)
        with open(public_path, 'a', encoding='utf-8') as f:
            f.write(content_public)
        print(f"Appended to public file: {public_path}")
    else:
        print(f"Duplicate public content found for {filename}, skipping")


    # Example usage
        
                        
    create_file_with_duplicate_check(
    extracted_text0=extracted_text0,
    extracted_text1=extracted_text1,
    extracted_text2=extracted_text2,
    final_name=final_name,
    simulation_result={"selections": selection},
    selection_result={"elem": selected_elements},
    random_size=random_size,
    calculate_hp=calculate_hp(),
    calculate_mana=calculate_mana(),
    atk_message=atk_message,
    def_message=def_message,
    agi_message=agi_message,
    int_message=int_message,
    wis_message=wis_message,
    chanceForSpecializedAdaptation=chanceForSpecializedAdaptation,
    calculate_atk=calculated_atk,
    calculate_def=calculated_def,
    calculate_agi=calculated_agi,
    calculate_int=calculated_int,
    calculate_wis=calculated_wis,
    random_bio=locals().get("random_bio"),
    random_ext=locals().get("random_ext"),
    summary_output_artist=summary_output_artist,
    summary_output_public=summary_output_public
)

content_artist = f"..."
content_public = f"..."

artist_dir = os.path.join("Output", "Artist", base_dir)
public_dir = os.path.join("Output", "Public", base_dir)
os.makedirs(artist_dir, exist_ok=True)
os.makedirs(public_dir, exist_ok=True)

filename = f"{subcat_abbr}_{date_str}.txt"

print("About to write files...")
print("Artist Dir:", artist_dir)
print("Public Dir:", public_dir)
print("Filename:", filename)

try:
    create_file_with_duplicate_check(artist_dir, public_dir, filename, content_artist, content_public)
except Exception as e:
    print("Error writing files:", e)

# Test file to confirm environment write ability
try:
    with open('test_output.txt', 'a', encoding='utf-8') as f:
        f.write("TEST WRITE\n")
    print("TEST WRITE successfully saved.")
except Exception as e:
    print("Error writing test file:", e)

    

    #User side, starts up and asks how many creatures you wanna make