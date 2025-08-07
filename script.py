import re
import random
import os
import hashlib
import datetime

#Global variables, lists
rerunYesNo = ["yes", "no"]

#directories = ["Creature_parts/BodyShapes/Amphibians",
#               "Creature_parts/BodyShapes/Birds",
#               "Creature_parts/BodyShapes/Fish",
#               "Creature_parts/BodyShapes/Invertebrates",
#               "Creature_parts/BodyShapes/Reptiles",
#               "Creature_parts/BodyShapes/Vertebrates"]
amphibians = "Creature_parts/BodyShapes/Amphibians"
birds = "Creature_parts/BodyShapes/Birds"
fish = "Creature_parts/BodyShapes/Fish"
invertebrates = "Creature_parts/BodyShapes/Invertebrates"
reptiles = "Creature_parts/BodyShapes/Reptiles"
vertebrates = "Creature_parts/BodyShapes/Vertebrates"

nameList1 = "Creature_parts/Genus.txt"
nameList2 = "Creature_parts/Epithet.txt"
nameList3 = "Creature_parts/Subspecies.txt"
nameList4 = "Creature_parts/Varietal.txt"
nameList5 = "Creature_parts/Behavioral.txt"

sizeList = ["Tiny", "Small", "Mid", "Large", "Giant", "Mega", "Super"]

typeList = ["Close", "Mid", "Range","Long Range", "Ground", "Water", "Lava/Magma", "Sky", "Underground", "Day", "Night", "Pack", "Group", "Horde"]
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
belPerc = [16.6, 16.6, 16.6, 16.6, 16.6, 16.6]
variantElementList = ["Strength", "Lightning", "Crystal", "Sharpness", "Ice", "Wind"]
velPerc = [16.6, 16.6, 16.6, 16.6, 16.6, 16.6]
higherElementList = ["Yin", "Yang"]
helPerc = [50, 50]
primordialElementList = ["Time", "Space", "Chaos"]
pelPerc = [33.3, 33.3, 33.3]
elementList = [basicElementList, variantElementList, higherElementList, primordialElementList]
elPerc = [70, 20, 7.5, 2.5]
promoting = {"Fire": "Earth", "Earth": "Gold", "Gold": "Water", "Water": "Wood", "Wood": "Fire"}
restraining = {"Fire": "Earth", "Earth": "Gold", "Gold": "Water", "Water": "Wood", "Wood": "Fire"}  # Same structure for simplicity
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

totalCreatedCreatures = 0
amountOfAmphibians = 0
amountOfBirds = 0
amountOfFish = 0
amountOfInvertebrates = 0
amountfOfReptiles = 0
amountOfVertebrates = 0
amountOfCreatures = int(input("How many creatures do you wanna make? "))
print(amountOfCreatures)

if __name__ == "__main__":
    
    while not totalCreatedCreatures == amountOfCreatures*6:
        print("Expected amount of Creatures", amountOfCreatures*6)
    #Random Body shape and random example 

        if (totalCreatedCreatures < amountOfCreatures):
            directory = amphibians
        elif (totalCreatedCreatures >= amountOfCreatures and totalCreatedCreatures < amountOfCreatures*2):
            directory = birds
        elif (totalCreatedCreatures >= amountOfCreatures*2 and totalCreatedCreatures < amountOfCreatures*3):
            directory = fish
        elif (totalCreatedCreatures >= amountOfCreatures*3 and totalCreatedCreatures < amountOfCreatures*4):
            directory = invertebrates
        elif (totalCreatedCreatures >= amountOfCreatures*4 and totalCreatedCreatures < amountOfCreatures*5):
            directory = reptiles
        elif (totalCreatedCreatures >= amountOfCreatures*5 and totalCreatedCreatures < amountOfCreatures*6):
            directory = vertebrates

        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

        random_file = os.path.join(directory, random.choice(files))

        def get_random_line(random_file):
            """Efficiently select a random line from a file."""
            line = None
            with open(random_file, 'r', encoding='utf-8') as f:
                for i, current_line in enumerate(f):
                    if random.randint(0, i) == 0:  # Reservoir sampling
                        line = current_line.strip()
            return line

        print(random_file)

        random_line = get_random_line(random_file)

        print(f"Random line: {random_line}")

        #Random Name
        def get_random_name(namelist):
            """Efficiently select a random line from a file."""
            name = None
            with open(namelist, 'r') as f:
                for i, current_name in enumerate(f):
                    if random.randint(0, i) == 0:  # Reservoir sampling
                        name = current_name.strip()
            return name

        random_name_amount = random.randint(1, 5)
        if (random_name_amount == 1):
            random_name1 = get_random_name(nameList1)
            final_name = [random_name1]
            print(final_name)
        elif (random_name_amount == 2):
            random_name1 = get_random_name(nameList1)
            random_name2 = get_random_name(nameList2)
            final_name = [random_name1, random_name2]
            print(final_name)
        elif (random_name_amount == 3):
            random_name1 = get_random_name(nameList1)
            random_name2 = get_random_name(nameList2)
            random_name3 = get_random_name(nameList3)
            final_name = [random_name1, random_name2, random_name3]
            print(final_name)
        elif (random_name_amount == 4):
            random_name1 = get_random_name(nameList1)
            random_name2 = get_random_name(nameList2)
            random_name3 = get_random_name(nameList3)
            random_name4 = get_random_name(nameList4)
            final_name = [random_name1, random_name2, random_name3, random_name4]
            print(final_name)
        elif (random_name_amount == 5):
            random_name1 = get_random_name(nameList1)
            random_name2 = get_random_name(nameList2)
            random_name3 = get_random_name(nameList3)
            random_name4 = get_random_name(nameList4)
            random_name5 = get_random_name(nameList5)
            final_name = [random_name1, random_name2, random_name3, random_name4, random_name5]
            print(final_name)

        #Random Size
        random_size = random.choice(sizeList)
        print(random_size)

        #Random Type
        # ====== Type Manager ======
        class ConflictFreeTypeSelector:
            def __init__(self):
                self.available = typeList.copy()
                self.selected = []
            
            def choose_type(self):
                if not self.available:
                    return None
                
                # Choose randomly from remaining types
                chosen = random.choice(self.available)
                self.selected.append(chosen)
                
                # Remove all conflicting types
                conflicts = interferingTypes.get(chosen, [])
                self.available = [t for t in self.available 
                                if t not in conflicts and t != chosen]
                
                return chosen
            
            def reset(self):
                self.available = typeList.copy()
                self.selected = []

        # ====== Simulation ======
        def run_simulation():
            selector = ConflictFreeTypeSelector()
            selections = []
            
            while selector.available:
                chosen = selector.choose_type()
                selections.append(chosen)
            print(f"Final Selection: {selections}")
            return selections

        # ====== Example Usage ======
        selection = run_simulation()

        #Specialized or Not
        def get_random_spec(speclist):
            """Efficiently select a random line from a file."""
            spec = None
            with open(speclist, 'r') as f:
                for i, current_spec in enumerate(f):
                    if random.randint(0, i) == 0:  # Reservoir sampling
                        spec = current_spec.strip()
            return spec

        chanceForSpecializedAdaptation = random.randint(1, 3)

        if (chanceForSpecializedAdaptation == 1):
            print("No Specialized Adaptation")
        elif (chanceForSpecializedAdaptation == 2):
            random_bio = get_random_spec(bioList)
            print("Bioluminescent " + random_bio)
        elif (chanceForSpecializedAdaptation == 3):
            random_ext = get_random_spec(extList)
            print("Extreme Camouflage " + random_ext)

        #Random Element(s)

        class ElementListManager:
            def __init__(self, items, initial_weights, list_type):
                self.items = items.copy()
                self.initial_weights = [w for w in initial_weights]
                self.available = self.items.copy()
                self.weights = self.initial_weights.copy()
                self.list_type = list_type  # e.g., "basic", "variant", etc.

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

        # ====== Global State ======
        selected_elements = []

        # ====== Weight Adjustment Logic ======
        def update_weights_based_on_rules(chosen_element, manager):
            # Adjust weights for promotion/restraint
            if chosen_element in promoting:
                promoted = promoting[chosen_element]
                if promoted in manager.available:
                    idx = manager.available.index(promoted)
                    manager.weights[idx] *= 1.1  # Boost promoted element

            if chosen_element in restraining:
                restrained = restraining[chosen_element]
                if restrained in manager.available:
                    idx = manager.available.index(restrained)
                    manager.weights[idx] *= 0.9  # Penalize restrained element
            
            #Adjust for derviving
            if chosen_element in derivedFrom:
                derived = derivedFrom[chosen_element]
                if derived in manager.available:
                    idx = manager.available.index(derived)
                    manager.weights[idx] *= 1.2

            # Adjust for Yin/Yang balance
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

        # ====== Main Logic ======
        def run_selection_process():
            global selected_elements
            managers = {
                "basic": ElementListManager(basicElementList, belPerc, "basic"),
                "variant": ElementListManager(variantElementList, velPerc, "variant"),
                "higher": ElementListManager(higherElementList, helPerc, "higher"),
                "primordial": ElementListManager(primordialElementList, pelPerc, "primordial")
            }

            multipleElements = False
            elements = 1
            while not multipleElements and elements != 4:

                valid_lists = elementList.copy()
                valid_weights = elPerc.copy()
                if random_size != "Super":
                    index = valid_lists.index(primordialElementList)
                    valid_weights.pop(index)
                    if primordialElementList in valid_lists:
                        valid_lists.remove(primordialElementList)
                # Choose list
                chosen_list = random.choices(valid_lists, weights=valid_weights, k=1)[0]
                list_name = None
                if chosen_list == basicElementList:
                    list_name = "basic"
                elif chosen_list == variantElementList:
                    list_name = "variant"
                elif chosen_list == higherElementList:
                    list_name = "higher"
                elif chosen_list == primordialElementList:
                    list_name = "primordial"

                # Choose element
                print(list_name)
                print(managers.keys())
                manager = managers[list_name]
                elem = manager.choose_element()
                if elem is None:
                    continue  # Skip if list is exhausted

                # Check for illegal combinations (e.g., Chaos + Time/Space)
                if elem == "Chaos" and any(e in selected_elements for e in illegalCombinations["Chaos"]):
                    print("Illegal combination! Resetting...")
                    selected_elements = []
                    return run_selection_process()  # Restart process

                selected_elements.append(elem)
                print(f"Selected: {elem}")

                # Update weights in all lists based on relationships
                for mgr in managers.values():
                    update_weights_based_on_rules(elem, mgr)

                # Rerun logic
                if list_name == "basic":
                    rerun = random.choices(rerunYesNo, weights=[60, 40], k=1)[0]
                elif list_name == "variant":
                    rerun = random.choices(rerunYesNo, weights=[25, 70], k=1)[0]
                elif list_name == "higher":
                    rerun = random.choices(rerunYesNo, weights=[10, 90], k=1)[0]
                elif list_name == "primordial":
                    rerun = random.choices(rerunYesNo, weights=[5, 95], k=1)[0]

                if rerun == "no":
                    multipleElements = True
                else:
                    elements += 1

            if elements == 4: elements -= 1
            print(f"Total elements selected: {elements}")
        run_selection_process()


        #Stats
        '''Tiny 5-8, Small 7-10, Mid 11-15, Large 17-22, Giant 25-30, Mega 37-50, Super 66-100. ATK, DEF, AGI, INT, WIS. HP = (DEF + (ATK*0.1)*10), MANA = (INT + (WIS*0.5)*5).'''

        stat_atk = 0
        def calculate_atk(base_atk):
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
            
            multipliers = []
            for element in selected_elements:
                if element in element_multipliers:
                    multipliers.append(element_multipliers[element])
            
            # Sort multipliers from highest to lowest
            multipliers.sort(reverse=True)
            
            result = base_atk
            for multiplier in multipliers:
                result *= multiplier
            
            return round(result, 1)
        stat_def = 0
        def calculate_def(base_def):
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
            
            multipliers = []
            for element in selected_elements:
                if element in element_multipliers:
                    multipliers.append(element_multipliers[element])
            
            # Sort multipliers from highest to lowest
            multipliers.sort(reverse=True)
            
            result = base_def
            for multiplier in multipliers:
                result *= multiplier
            
            return round(result, 1)
        stat_agi = 0
        def calculate_agi(base_agi):
            element_multipliers = {
                "Lightning": 1.250,
                "Wind": 1.350,
                "Water": 1.250,
                "Chaos": 2.100
            }
            
            multipliers = []
            for element in selected_elements:
                if element in element_multipliers:
                    multipliers.append(element_multipliers[element])
            
            # Sort multipliers from highest to lowest
            multipliers.sort(reverse=True)
            
            result = base_agi
            for multiplier in multipliers:
                result *= multiplier
            
            return round(result, 1)
        stat_int = 0
        def calculate_int(base_int):
            element_multipliers = {
                "Fire": 1.100,
                "Yang": 1.500,
                "Gold": 1.200,
                "Yin": 1.500,
                "Water": 1.25,
                "Space": 2.300,
                "Ice": 1.270
            }
            
            multipliers = []
            for element in selected_elements:
                if element in element_multipliers:
                    multipliers.append(element_multipliers[element])
            
            # Sort multipliers from highest to lowest
            multipliers.sort(reverse=True)
            
            result = base_int
            for multiplier in multipliers:
                result *= multiplier
            
            return round(result, 1)
        stat_wis = 0
        def calculate_wis(base_wis):
            element_multipliers = {
                "Yang": 1.500,
                "Yin": 1.500,
                "Wood": 1.300,
                "Time": 2.500
            }
            
            multipliers = []
            for element in selected_elements:
                if element in element_multipliers:
                    multipliers.append(element_multipliers[element])
            
            # Sort multipliers from highest to lowest
            multipliers.sort(reverse=True)
            
            result = base_wis
            for multiplier in multipliers:
                result *= multiplier
            
            return round(result, 1)

        def calculate_hp():
            return round(((stat_def + (stat_atk*0.1))*10), 1) #Works

        def calculate_mana():
            return round(((stat_int + (stat_wis*0.5))*5), 1) #Works

        if (random_size == "Tiny"):
            stat_atk = random.randint(5, 8)
            stat_def = random.randint(5, 8)
            stat_agi = random.randint(5, 8)
            stat_int = random.randint(5, 8)
            stat_wis = random.randint(5, 8)
            calculated_atk = calculate_atk(stat_atk)
            calculated_def = calculate_def(stat_def)
            calculated_agi = calculate_agi(stat_agi)
            calculated_int = calculate_int(stat_int)
            calculated_wis = calculate_wis(stat_wis)

            if (calculated_atk != stat_atk):
                atk_message = f"ATK: {calculated_atk:.1f} because of elemental bonuses, base ATK: {stat_atk:.1f}"
            else:
                atk_message = f"ATK: {stat_atk:.1f}"

            if (calculated_def != stat_def):
                def_message = f"DEF: {calculated_def:.1f} because of elemental bonuses, base DEF: {stat_def:.1f}"
            else:
                def_message = f"DEF: {stat_def:.1f}"

            if (calculated_agi != stat_agi):
                agi_message = f"AGI: {calculated_agi:.1f} because of elemental bonuses, base AGI: {stat_agi:.1f}"
            else:
                agi_message = f"AGI: {stat_agi:.1f}"
            
            if (calculated_int != stat_int):
                int_message = f"INT: {calculated_int:.1f} because of elemental bonuses, base INT: {stat_int:.1f}"
            else:
                int_message = f"INT: {stat_int:.1f}"

            if (calculated_wis != stat_wis):
                wis_message = f"WIS: {calculated_wis:.1f} because of elemental bonuses, base WIS: {stat_wis:.1f}"
            else:
                wis_message = f"WIS: {stat_wis:.1f}"

            print(f"Stats: /n {atk_message} \n {def_message} \n {agi_message} \n {int_message} \n {wis_message} \n HP: {calculate_hp()} MANA: {calculate_mana()}")

        elif(random_size == "Small"):
            stat_atk = random.randint(7, 10)
            stat_def = random.randint(7, 10)
            stat_agi = random.randint(7, 10)
            stat_int = random.randint(7, 10)
            stat_wis = random.randint(7, 10)
            calculated_atk = calculate_atk(stat_atk)
            calculated_def = calculate_def(stat_def)
            calculated_agi = calculate_agi(stat_agi)
            calculated_int = calculate_int(stat_int)
            calculated_wis = calculate_wis(stat_wis)

            if (calculated_atk != stat_atk):
                atk_message = f"ATK: {calculated_atk:.1f} because of elemental bonuses, base ATK: {stat_atk:.1f}"
            else:
                atk_message = f"ATK: {stat_atk:.1f}"

            if (calculated_def != stat_def):
                def_message = f"DEF: {calculated_def:.1f} because of elemental bonuses, base DEF: {stat_def:.1f}"
            else:
                def_message = f"DEF: {stat_def:.1f}"

            if (calculated_agi != stat_agi):
                agi_message = f"AGI: {calculated_agi:.1f} because of elemental bonuses, base AGI: {stat_agi:.1f}"
            else:
                agi_message = f"AGI: {stat_agi:.1f}"
            
            if (calculated_int != stat_int):
                int_message = f"INT: {calculated_int:.1f} because of elemental bonuses, base INT: {stat_int:.1f}"
            else:
                int_message = f"INT: {stat_int:.1f}"

            if (calculated_wis != stat_wis):
                wis_message = f"WIS: {calculated_wis:.1f} because of elemental bonuses, base WIS: {stat_wis:.1f}"
            else:
                wis_message = f"WIS: {stat_wis:.1f}"
            
            print(f"Stats: \n {atk_message} \n {def_message} \n {agi_message} \n {int_message} \n {wis_message} \n HP: {calculate_hp()} MANA: {calculate_mana()}")

        elif(random_size == "Mid"):
            stat_atk = random.randint(11, 15)
            stat_def = random.randint(11, 15)
            stat_agi = random.randint(11, 15)
            stat_int = random.randint(11, 15)
            stat_wis = random.randint(11, 15)
            calculated_atk = calculate_atk(stat_atk)
            calculated_def = calculate_def(stat_def)
            calculated_agi = calculate_agi(stat_agi)
            calculated_int = calculate_int(stat_int)
            calculated_wis = calculate_wis(stat_wis)

            if (calculated_atk != stat_atk):
                atk_message = f"ATK: {calculated_atk:.1f} because of elemental bonuses, base ATK: {stat_atk:.1f}"
            else:
                atk_message = f"ATK: {stat_atk:.1f}"

            if (calculated_def != stat_def):
                def_message = f"DEF: {calculated_def:.1f} because of elemental bonuses, base DEF: {stat_def:.1f}"
            else:
                def_message = f"DEF: {stat_def:.1f}"

            if (calculated_agi != stat_agi):
                agi_message = f"AGI: {calculated_agi:.1f} because of elemental bonuses, base AGI: {stat_agi:.1f}"
            else:
                agi_message = f"AGI: {stat_agi:.1f}"
            
            if (calculated_int != stat_int):
                int_message = f"INT: {calculated_int:.1f} because of elemental bonuses, base INT: {stat_int:.1f}"
            else:
                int_message = f"INT: {stat_int:.1f}"

            if (calculated_wis != stat_wis):
                wis_message = f"WIS: {calculated_wis:.1f} because of elemental bonuses, base WIS: {stat_wis:.1f}"
            else:
                wis_message = f"WIS: {stat_wis:.1f}"
            
            print(f"Stats: \n {atk_message} \n {def_message} \n {agi_message} \n {int_message} \n {wis_message} \n HP: {calculate_hp()} MANA: {calculate_mana()}")

        elif(random_size == "Large"):
            stat_atk = random.randint(17, 22)
            stat_def = random.randint(17, 22)
            stat_agi = random.randint(17, 22)
            stat_int = random.randint(17, 22)
            stat_wis = random.randint(17, 22)
            calculated_atk = calculate_atk(stat_atk)
            calculated_def = calculate_def(stat_def)
            calculated_agi = calculate_agi(stat_agi)
            calculated_int = calculate_int(stat_int)
            calculated_wis = calculate_wis(stat_wis)

            if (calculated_atk != stat_atk):
                atk_message = f"ATK: {calculated_atk:.1f} because of elemental bonuses, base ATK: {stat_atk:.1f}"
            else:
                atk_message = f"ATK: {stat_atk:.1f}"

            if (calculated_def != stat_def):
                def_message = f"DEF: {calculated_def:.1f} because of elemental bonuses, base DEF: {stat_def:.1f}"
            else:
                def_message = f"DEF: {stat_def:.1f}"

            if (calculated_agi != stat_agi):
                agi_message = f"AGI: {calculated_agi:.1f} because of elemental bonuses, base AGI: {stat_agi:.1f}"
            else:
                agi_message = f"AGI: {stat_agi:.1f}"
            
            if (calculated_int != stat_int):
                int_message = f"INT: {calculated_int:.1f} because of elemental bonuses, base INT: {stat_int:.1f}"
            else:
                int_message = f"INT: {stat_int:.1f}"

            if (calculated_wis != stat_wis):
                wis_message = f"WIS: {calculated_wis:.1f} because of elemental bonuses, base WIS: {stat_wis:.1f}"
            else:
                wis_message = f"WIS: {stat_wis:.1f}"
            
            print(f"Stats: \n {atk_message} \n {def_message} \n {agi_message} \n {int_message} \n {wis_message} \n HP: {calculate_hp()} MANA: {calculate_mana()}")

        elif(random_size == "Giant"):
            stat_atk = random.randint(25, 30)
            stat_def = random.randint(25, 30)
            stat_agi = random.randint(25, 30)
            stat_int = random.randint(25, 30)
            stat_wis = random.randint(25, 30)
            calculated_atk = calculate_atk(stat_atk)
            calculated_def = calculate_def(stat_def)
            calculated_agi = calculate_agi(stat_agi)
            calculated_int = calculate_int(stat_int)
            calculated_wis = calculate_wis(stat_wis)

            if (calculated_atk != stat_atk):
                atk_message = f"ATK: {calculated_atk:.1f} because of elemental bonuses, base ATK: {stat_atk:.1f}"
            else:
                atk_message = f"ATK: {stat_atk:.1f}"

            if (calculated_def != stat_def):
                def_message = f"DEF: {calculated_def:.1f} because of elemental bonuses, base DEF: {stat_def:.1f}"
            else:
                def_message = f"DEF: {stat_def:.1f}"

            if (calculated_agi != stat_agi):
                agi_message = f"AGI: {calculated_agi:.1f} because of elemental bonuses, base AGI: {stat_agi:.1f}"
            else:
                agi_message = f"AGI: {stat_agi:.1f}"
            
            if (calculated_int != stat_int):
                int_message = f"INT: {calculated_int:.1f} because of elemental bonuses, base INT: {stat_int:.1f}"
            else:
                int_message = f"INT: {stat_int:.1f}"

            if (calculated_wis != stat_wis):
                wis_message = f"WIS: {calculated_wis:.1f} because of elemental bonuses, base WIS: {stat_wis:.1f}"
            else:
                wis_message = f"WIS: {stat_wis:.1f}"
            
            print(f"Stats: \n {atk_message} \n {def_message} \n {agi_message} \n {int_message} \n {wis_message} \n HP: {calculate_hp()} MANA: {calculate_mana()}")

        elif(random_size == "Mega"):
            stat_atk = random.randint(37, 50)
            stat_def = random.randint(37, 50)
            stat_agi = random.randint(37, 50)
            stat_int = random.randint(37, 50)
            stat_wis = random.randint(37, 50)
            calculated_atk = calculate_atk(stat_atk)
            calculated_def = calculate_def(stat_def)
            calculated_agi = calculate_agi(stat_agi)
            calculated_int = calculate_int(stat_int)
            calculated_wis = calculate_wis(stat_wis)

            if (calculated_atk != stat_atk):
                atk_message = f"ATK: {calculated_atk:.1f} because of elemental bonuses, base ATK: {stat_atk:.1f}"
            else:
                atk_message = f"ATK: {stat_atk:.1f}"

            if (calculated_def != stat_def):
                def_message = f"DEF: {calculated_def:.1f} because of elemental bonuses, base DEF: {stat_def:.1f}"
            else:
                def_message = f"DEF: {stat_def:.1f}"

            if (calculated_agi != stat_agi):
                agi_message = f"AGI: {calculated_agi:.1f} because of elemental bonuses, base AGI: {stat_agi:.1f}"
            else:
                agi_message = f"AGI: {stat_agi:.1f}"
            
            if (calculated_int != stat_int):
                int_message = f"INT: {calculated_int:.1f} because of elemental bonuses, base INT: {stat_int:.1f}"
            else:
                int_message = f"INT: {stat_int:.1f}"

            if (calculated_wis != stat_wis):
                wis_message = f"WIS: {calculated_wis:.1f} because of elemental bonuses, base WIS: {stat_wis:.1f}"
            else:
                wis_message = f"WIS: {stat_wis:.1f}"
            
            print(f"Stats: \n {atk_message} \n {def_message} \n {agi_message} \n {int_message} \n {wis_message} \n HP: {calculate_hp()} MANA: {calculate_mana()}")

        elif(random_size == "Super"):
            stat_atk = random.randint(66, 100)
            stat_def = random.randint(66, 100)
            stat_agi = random.randint(66, 100)
            stat_int = random.randint(66, 100)
            stat_wis = random.randint(66, 100)
            calculated_atk = calculate_atk(stat_atk)
            calculated_def = calculate_def(stat_def)
            calculated_agi = calculate_agi(stat_agi)
            calculated_int = calculate_int(stat_int)
            calculated_wis = calculate_wis(stat_wis)

            if (calculated_atk == stat_atk):
                atk_message = f"ATK: {calculated_atk:.1f} because of elemental bonuses, base ATK: {stat_atk:.1f}"
            else:
                atk_message = f"ATK: {stat_atk:.1f}"
            
            if (calculated_def != stat_def):
                def_message = f"DEF: {calculated_def:.1f} because of elemental bonuses, base DEF: {stat_def:.1f}"
            else:
                def_message = f"DEF: {stat_def:.1f}"

            if (calculated_agi != stat_agi):
                agi_message = f"AGI: {calculated_agi:.1f} because of elemental bonuses, base AGI: {stat_agi:.1f}"
            else:
                agi_message = f"AGI: {stat_agi:.1f}"
            
            if (calculated_int != stat_int):
                int_message = f"INT: {calculated_int:.1f} because of elemental bonuses, base INT: {stat_int:.1f}"
            else:
                int_message = f"INT: {stat_int:.1f}"

            if (calculated_wis != stat_wis):
                wis_message = f"WIS: {calculated_wis:.1f} because of elemental bonuses, base WIS: {stat_wis:.1f}"
            else:
                wis_message = f"WIS: {stat_wis:.1f}"
            
            print(f"Stats: \n {atk_message} \n {def_message} \n {agi_message} \n {int_message} \n {wis_message} \n HP: {calculate_hp()} MANA: {calculate_mana()}")



        #search Required_Text.txt file and get its info

        target_filename = random_file
        search_file0 = "Required_Text0.txt" 
        search_file1 = "Required_Text1.txt"
        search_file2 = "Required_Text2.txt"

        pattern = re.compile(
            rf"^.*?\b{re.escape(target_filename)}\b.*?=\s*(.*?)\s*(#|$)", 
            re.IGNORECASE
        )

        try:
            with open(search_file0, "r") as f:
                for line_num, line in enumerate(f, 1):
                    #print(f"Checking line {line_num}: {line.strip()}")  # Debug: Show scanned lines
                    match = pattern.search(line)
                    if match:
                        extracted_text0 = match.group(1).strip()
                        print(f"\nMATCH FOUND! Extracted text 0: '{extracted_text0}'")
                        break
            print("\nScript finished. If no match was found, check the regex pattern or file content.")
        except FileNotFoundError:
            print(f"Error: File '{search_file0}' not found.")
        except Exception as e:
            print(f"Error: {e}")

        try:
            with open(search_file1, "r") as f:
                for line_num, line in enumerate(f, 1):
                    #print(f"Checking line {line_num}: {line.strip()}")  # Debug: Show scanned lines
                    match = pattern.search(line)
                    if match:
                        extracted_text1 = match.group(1).strip()
                        print(f"\nMATCH FOUND! Extracted text 1: '{extracted_text1}'")
                        break
            print("\nScript finished. If no match was found, check the regex pattern or file content.")
        except FileNotFoundError:
            print(f"Error: File '{search_file1}' not found.")
        except Exception as e:
            print(f"Error: {e}")

        try:
            with open(search_file2, "r") as f:
                for line_num, line in enumerate(f, 1):
                    #print(f"Checking line {line_num}: {line.strip()}")  # Debug: Show scanned lines
                    match = pattern.search(line)
                    if match:
                        extracted_text2 = match.group(1).strip()
                        print(f"\nMATCH FOUND! Extracted text 2: '{extracted_text2}'")
                        break
            print("\nScript finished. If no match was found, check the regex pattern or file content.")
        except FileNotFoundError:
            print(f"Error: File '{search_file2}' not found.")
        except Exception as e:
            print(f"Error: {e}")


        #temp
        def get_file_hash(file_path):
            """Calculate SHA-256 hash of a file in chunks to handle large files."""
            sha256 = hashlib.sha256()
            try:
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(65536)  # Read in 64KB chunks
                        if not chunk:
                            break
                        sha256.update(chunk)
                return sha256.hexdigest()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                return None

        def is_content_duplicate(directory, content):
            """Check if content already exists in any file in the directory or subdirectories."""
            if not os.path.exists(directory):
                return False
                
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            
            for root, _, files in os.walk(directory):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    if get_file_hash(file_path) == content_hash:
                        return True
            return False

    def create_file_with_duplicate_check(extracted_text0, extracted_text1, extracted_text2, final_name, 
                                        simulation_result, selection_result, random_size, 
                                        calculate_hp, calculate_mana, atk_message, def_message, 
                                        agi_message, int_message, wis_message, chanceForSpecializedAdaptation,
                                        calculate_atk, calculate_def, calculate_agi, calculate_int, calculate_wis,
                                        random_bio=None, random_ext=None):
        """Create artist and public files with deduplication in category-specific directories."""
        CATEGORY_MAP = {
            "Vertebrate": {
                "subcategories": {
                    "Arboreal Quadrupedal": "AQ",
                    "Cursorial Quadrupedal": "CQ",
                    "Fossorial Quadrupedal": "FQ",
                    "Graviportal Quadrupedal": "GQ",
                    "Semi-Aquatic Quadrupedal": "SAQ"
                },
                "base_path": "Vertebrate"
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
            "Amphibian": {
                "subcategories": {
                    "Aquatic Paedomorphic": "AP",
                    "Arboreal Frog": "AF",
                    "Fossorial Amphibian": "FA"
                },
                "base_path": "Amphibians"
            }
        }
        
        # Get category configuration
        category_config = CATEGORY_MAP.get(extracted_text1)
        if not category_config:
            raise ValueError(f"Invalid category: {extracted_text1}")

        # Get subcategory abbreviation
        subcat_abbr = category_config["subcategories"].get(extracted_text0)
        if not subcat_abbr:
            raise ValueError(f"Invalid subcategory for {extracted_text1}: {extracted_text0}")

        # Create directory paths
        base_dir = category_config["base_path"]
        artist_dir = os.path.join("Output", "Artist", base_dir)
        public_dir = os.path.join("Output", "Public", base_dir)

        # Create directories if they don't exist
        os.makedirs(artist_dir, exist_ok=True)
        os.makedirs(public_dir, exist_ok=True)

        # Generate filename with date only (no timestamp)
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        filename = f"{subcat_abbr}_{date_str}.txt"

        # Generate specialized adaptation strings
        if chanceForSpecializedAdaptation == 1:
            specialized_public = 'no'
            specialized_artist = 'no'
        elif chanceForSpecializedAdaptation == 2:
            specialized_public = 'Bioluminescent'
            specialized_artist = f'Bioluminescent: {random_bio}' if random_bio else 'Bioluminescent'
        elif chanceForSpecializedAdaptation == 3:
            specialized_public = 'Extreme Camouflage'
            specialized_artist = f'Extreme Camouflage: {random_ext}' if random_ext else 'Extreme Camouflage'
        else:
            specialized_public = 'unknown'
            specialized_artist = 'unknown'

        # Generate content
        separator_artist_start = "🖌️"
        separator_artist_end = "❎"
        separator_artist_upper = "x-" * 48
        separator_artist_lower = "-x" * 48
        separator_public_upper = "-x" * 49
        separator_public_lower = "x-" * 49

        content_artist = (
            f"{separator_artist_start}{separator_artist_upper}{separator_artist_end}\n"
            f"Name: {final_name}\n"
            f"Shape: {extracted_text1}, {extracted_text0}, {extracted_text2}\n"
            f"Type: {', '.join(simulation_result.get('selections', []))}\n"
            f"Size: {random_size}\n"
            f"Element(s): {', '.join(selection_result.get('elem', []))}\n"
            "Stats: \n"
            f"HP: {calculate_hp}  MANA: {calculate_mana}\n"
            f"ATK: {atk_message}\n"
            f"DEF: {def_message}\n"
            f"AGI: {agi_message}\n"
            f"INT: {int_message}\n"
            f"WIS: {wis_message}\n"
            f"Specialized: {specialized_artist}\n"
            f"{separator_artist_start}{separator_artist_lower}{separator_artist_end}\n"
        )

        content_public = (
            f"{separator_public_upper}\n"
            f"Name: {final_name}\n"
            f"Shape: {extracted_text1}\n"
            f"Type: {', '.join(simulation_result.get('selections', []))}\n"
            f"Size: {random_size}\n"
            f"Element(s): {', '.join(selection_result.get('elem', []))}\n"
            "Stats: \n"
            f"HP: {calculate_hp}  MANA: {calculate_mana}\n"
            f"ATK: {calculate_atk}\n"
            f"DEF: {calculate_def}\n"
            f"AGI: {calculate_agi}\n"
            f"INT: {calculate_int}\n"
            f"WIS: {calculate_wis}\n"
            f"Specialized: {specialized_public}\n"
            f"{separator_public_lower}\n"
        )

        # Write files with deduplication check
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
        
        
        create_file_with_duplicate_check()
                        

    

    #User side, starts up and asks how many creatures you wanna make

    totalCreatedCreatures += 1