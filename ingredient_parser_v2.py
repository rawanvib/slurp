import re
import unicodedata
import fractions
import string


# converts fraction value to float
def mixed_to_float(x):
    return float(sum(fractions.Fraction(term) for term in x.split()))


def get_string(num):
    num = float(num)
    if num % 1 == 0:
        num = str(int(num))
    else:
        num = str(round(num, 2))
    return num


NUMBERS = {"one": "1", "One": '1', "two": '2', "Two": '2', "three": '3', "Three": '3', "half": '0.5', "Half": '0.5'}
JOIN_NUMBERS = {"one and half": '1.5', "One and a half": '1.5', "one and a half": '1.5', "one half": '1.5',
                "two and half": '2.5', "two half": '2.5',
                "three and half": '3.5', "three half": '3.5',
                "one fourth": '0.25', "One fourth": '0.25',
                "three fourth": '0.75', "Three fourth": '0.75'
                }

#         "\d+\s*to\s*\d+\s*\d*\/\s*\d+|"
# parse the quantity from name
base_qty = "\d+\s*(\d*\/\s*\d+)*\s*"


def parse_qty(name):
    qty = [(m.start(0), str(m.group())) for m in re.finditer(
        "("
        "(\d+\s*(\d*[.\/]\d+)*\s*(\+|and)\s*\d+\s*(\d*[.\/]\d+)*)|"
        "\d+\s*(\d*\s*[.\/]\s*\d+)*\s*(-|to|or)\s*\d+\s*(\d*\s*[.\/]\s*\d+)*|"
        "\d+\s+\d[.]\d+|"
        "\d+([.]\d+)*\s*\-\s*\d+([.]\d+)*|"
        "\d+\s*to\s*\d+|"
        "\d+\s*or\s*\d+|"
        "\d+\s*\d*\/\d+|"
        "\d+\.\d+|"
        "[.]\d+|"
        "\d+"
        ")*",
        name) if m.group() != '']
    # qty = [i[0] for i in qty if i[0] != '']
    final_qty = []
    og_name = name
    for one_qty in qty:
        one_qty = list(one_qty)
        # _index = og_name.index(one_qty)
        name = name.replace(one_qty[1], " ", 1)
        og_qty = one_qty[1]
        one_qty[1] = re.sub(r"\s*\/\s*", "/", one_qty[1])
        # for converting 1-1/2 ,1 to 1.5 ,1/2 to 2, 4 or 5
        if re.match(r"(\d+\s*(\d*\s*[.\/]\s*\d+)*\s*(-|to|or)\s*\d+\s*(\d*\s*[.\/]\s*\d+)*)", one_qty[1]):
            cleaned_qty = re.sub(r"\s*(or|to)\s*", "-", one_qty[1])
            temp = cleaned_qty.split("-")
            temp[0] = get_string(mixed_to_float(temp[0]))
            temp[1] = get_string(mixed_to_float(temp[1]))
            cleaned_qty = "-".join(temp)
        # for converting 5+1 to 6  , 1 and 2
        elif re.match("(\d+\s*(\d*[.\/]\d+)*\s*(\+|and)\s*\d+\s*(\d*[.\/]\d+)*)", one_qty[1]):
            cleaned_qty = re.sub(r"(\+|and)", "+", one_qty[1])
            temp = cleaned_qty.split("+")
            temp = [n for n in temp if n != ""]
            cleaned_qty = get_string(mixed_to_float(temp[0]) + mixed_to_float(temp[1]))
        # for converting to 1 0.5 to 1.5
        elif re.match("\d+\s+\d+[.]\d+", one_qty[1]):
            temp = one_qty[1].split(" ")
            temp = [n for n in temp if n != ""]
            cleaned_qty = get_string(float(temp[0]) + float(temp[1]))
        # for .66 to 0.66
        elif re.match(r"[.]\d+", one_qty[1]):
            cleaned_qty = "0" + one_qty[1]
        # for only 1 1/2
        elif re.match("\d+\s*\d*\/\d+", one_qty[1]):
            cleaned_qty = get_string(mixed_to_float(one_qty[1]))
        else:
            cleaned_qty = get_string(mixed_to_float(one_qty[1]))
        cleaned_qty = re.sub("\s+", " ", cleaned_qty)
        out_dict = {
            "og_qty": og_qty,
            "cleaned_qty": cleaned_qty,
            "index": one_qty[0]
        }
        final_qty.append(out_dict)
    # for pattern like "one and half"
    for join_number in JOIN_NUMBERS.keys():
        if_present = name.find(join_number)
        if if_present != -1:
            cleaned_qty = str(JOIN_NUMBERS[join_number])
            _index = og_name.index(join_number)

            name = name.replace(join_number, " ")
            out_dict = {
                "og_qty": join_number,
                "cleaned_qty": cleaned_qty,
                "index": _index
            }
            final_qty.append(out_dict)
    # for pattern like "one","two"
    name_list = name.split(" ")
    for word in name_list:
        if word in NUMBERS.keys():
            cleaned_qty = NUMBERS[word]
            name = name.replace(word, " ")
            _index = og_name.index(word)
            out_dict = {
                "og_qty": cleaned_qty,
                "cleaned_qty": cleaned_qty,
                "index": _index
            }
            final_qty.append(out_dict)
    return final_qty, name


# for cleaning ingredients

UNITS = {"cup": ["cups", "cup","c.","c"],   #c,c.
         "gallon": ["gal", "gal.", "gallon", "gallons"],
         "ounce": ["oz", "oz.", "ounce", "ounces"],
         "pint": ["pt", "pt.", "pint", "pints"],
         "pound": ["lb", "lb.", "lbs", "pound", "pounds"],
         "quart": ["qt", "qt.", "qts", "qts.", "quart", "quarts"],
         "tablespoon": ["tbsp.", "tbsp", "tbsp,", "tablespoon", "tablespoons", "tbs.", "tbs", "tbs,", "tbsps", "tblsp",
                        "tbpn","tb"],                                                                        #tb
         "teaspoon": ["tsp.", "tsp", "tsp,", "teaspoon", "teaspoons", "tsps", "tspn","ts"],              #ts
         "spoon": ["spoon", "spoons", "spn"],
         "gram": ["gr", "gr.", "grams", 'grams,', 'gms', 'gm', 'g'],
         "kilogram": ["kg", "kg.", "kilogram", "kilograms", "kilo", "kgs"],
         "liter": ["liter", "liters", "litre", "litres", "ltr", "ltrs", "L"],
         "milligram": ["mg", "mg.", "milligram", "milligrams"],
         "milliliter": ["ml", "ml.", "mls", "milliliter", "milliliters"],
         "centiliter": ["cl", "cl."],
         "centimeter": ['cm', 'cms'],
         "pinch": ["pinch", "pinches"],
         "dash": ["dash", "dashes"],
         "stick": ["stick", "sticks"],
         "can": ["cans", "can"],
         "scoop": ["scoop", "scoops"],
         "filets": ["filet", "filets"],
         "sprig": ["sprigs", "sprig"],
         "piece": ["pcs", "pc"],
         "inch": ["inch", "inches"],
         "glass": ["glass", "glasses"],
         "bunch": ["bunch", "bunches"],
         "stalk": ["stalk"],
         "flakes": ["flakes"],
         "tin": ["tin"],
         "shot": ["shots", "shot"],
         "part": ["parts", "part"],
         "No.s": ["nos", "no"],
         "drop": ["drops", "drop"]}

# 2 word units
UNITS2 = {
    "fluid_ounce": ["fl. oz.", "fl oz", "fluid ounces", "fluid ounce"],
    "tablespoon": ["Table spoons", "table spoons",
                   "table Spoons", "Table Spoons", "Table spoon", "table spoon", "table Spoon", "Table Spoon",
                   "tbl spn"],
    "teaspoon": ["Tea spoons", "tea spoons", "tea Spoons",
                 "Tea Spoons", "Tea spoon", "tea spoon", "tea Spoon", "Tea Spoon"],
    "inch": ["inch pieces", "inch piece"],
    "milliliter": ['milli liters', 'milli liter']
}

# low priority units
UNITS3 = {"As required": ["to taste", "as required", "To taste", "As required", "as per taste", "according to taste",
                          "as per your taste"],
          "No.s": ["numbers", "number", "Number", "Numbers", "nos"],
          "piece": ["pieces", "piece"],
          "A pinch": ["A pinch", "a pinch"],
          }


def replace_str_index_to(text, index, end_index):
    output = ''
    # end_index = end_index + 1
    for i, j in enumerate(text):
        if index <= i < end_index:
            output = output + " "
        else:
            output = output + j
    return output


def match_unit_qty(qty, unit_index, name, og_unit):
    _index = None
    dist = 1000
    out_qty = None
    if len(qty):
        if unit_index is not None:
            for qty_index, one_qty in enumerate(qty):
                tmep_dist = abs(unit_index - (int(one_qty['index']) + 2))
                if unit_index == one_qty['index']:
                    tmep_dist = 0
                if tmep_dist <= dist and one_qty["cleaned_qty"] not in ['0', '00', '000']:
                    dist = tmep_dist
                    _index = qty_index
            qty_start = qty[_index]['index']
            qty_end = qty[_index]['index'] + len(qty[_index]['og_qty'])
            unit_start = unit_index
            unit_end = unit_index + len(og_unit)
            name = replace_str_index_to(name, qty_start, qty_end)
            for i in [' a ', ' or ', ' of ', ' x ', ' to ']:
                if (qty_start - 4) >= 0:
                    if name[qty_start - 4:qty_start].find(i) != -1:
                        name = replace_str_index_to(name, qty_start - len(i), qty_start)
                if qty_end + 4 <= len(name):
                    if name[qty_end:qty_end + 4].find(i) != -1:
                        name = replace_str_index_to(name, qty_end, qty_end + len(i))
            name = replace_str_index_to(name, unit_start, unit_end)
            for i in [' a ', ' or ', ' of ', ' x ', ' to ']:
                if (unit_start - 4) >= 0:
                    if name[unit_start - 4:unit_start].find(i) != -1:
                        name = replace_str_index_to(name, unit_start - len(i), unit_start)
                if unit_end + 4 <= len(name):
                    if name[unit_end:unit_end + 4].find(i) != -1:
                        name = replace_str_index_to(name, unit_end, unit_end + len(i))
            out_qty = qty[_index]["cleaned_qty"]
        else:
            qty_start = qty[0]['index']
            qty_end = qty[0]['index'] + len(qty[0]['og_qty'])
            name = replace_str_index_to(name, qty_start, qty_end)
            for i in [' a ', ' or ', ' of ', ' x ', ' to ']:
                if (qty_start - 4) >= 0:
                    if name[qty_start - 4:qty_start].find(i) != -1:
                        name = replace_str_index_to(name, qty_start - len(i), qty_start)
                if qty_end + 4 <= len(name):
                    if name[qty_end:qty_end + 4].find(i) != -1:
                        name = replace_str_index_to(name, qty_end, qty_end + len(i))
            out_qty = qty[0]["cleaned_qty"]
    return name, out_qty


# parse unit from name
def parse_unit(name):
    # replace '&' with 'and' , '-'  from name cannot remove before quantity cal.
    name = name.replace("-", " ")
    og_name = name
    units_found = None
    og_unit = None
    unit_index = None
    for key_unit in UNITS2.keys():
        if units_found is None:
            for unit in UNITS2[key_unit]:
                if_present = name.find(unit)
                if if_present != -1:
                    unit_index = if_present
                    units_found = key_unit
                    og_unit = unit
                    break
    name = name.split(" ")
    name = [n for n in name if n != ""]
    for token_name in name:
        if units_found is None:
            for one_unit in UNITS.keys():
                for key_unit in UNITS[one_unit]:
                    # ',' to be removed if attached with unit
                    comma_removed = re.sub(r"[^A-Za-z]", "", token_name)
                    if comma_removed.lower() == key_unit.lower():
                        # remove 'of','to','a','or' around unit
                        _index = og_name.find(token_name)
                        if token_name.find(comma_removed + ".") != -1:
                            only_unit_index = token_name.find(comma_removed + ".")
                            comma_removed = comma_removed+"."
                        else:
                            only_unit_index = token_name.find(comma_removed)
                        if _index != -1 and only_unit_index != -1:
                            unit_index = only_unit_index + _index
                        units_found = one_unit
                        og_unit = comma_removed
    name = " ".join(name)
    for key_unit in UNITS3.keys():
        if units_found is None:
            for unit in UNITS3[key_unit]:
                if_present = name.find(unit)
                if if_present != -1:
                    unit_index = if_present
                    units_found = key_unit
                    og_unit = unit
                    break
    return units_found, unit_index, og_unit


# string replacement at specific index
def replace_str_index(text, index=0, replacement=''):
    return '%s%s%s' % (text[:index], replacement, text[index + 1:])


conjunctions = ['after', 'although', 'as', 'as long as', 'though', 'because', 'before', 'if', 'though', 'that', 'lest',
                'once', 'since', 'so', 'that', 'than', 'though', 'till', 'unless', 'until', 'when', 'whenever', 'where',
                'whereas', 'wherever', 'for', 'nor', 'but', 'or', 'yet', 'so', 'in', 'on', 'of', 'and', 'to', 'x']


# cleaning name by leading ,trailing special chars
def cleaned_name(name1):
    name = name1.strip()
    name = name.replace("  ", " ")
    name = name.replace("&", "and")
    name = name.replace("-", " ")
    if name:
        if not name[0].isalnum():
            name = replace_str_index(name, 0)
            name = name.strip()
        if name:
            if not name[-1].isalnum():
                name = replace_str_index(name, len(name) - 1)
                name = name.strip()
        name_split = name.split(" ")
        if name_split:
            if name_split[0] in conjunctions:
                del name_split[0]
        if name_split:
            if name_split[-1] in conjunctions:
                del name_split[-1]
        name = " ".join(name_split)
    if name == name1:
        return name.strip()
    else:
        return cleaned_name(name)


def ingredient_preprocess(name):
    name = re.sub(r'\([^)]*\)', '', name)
    name = name.replace("\n", " ")
    name = name.replace(" half", " 1/2")
    # new_name = []
    name = unicodedata.normalize('NFKD', name).replace('⁄', "/")
    # name = re.sub(r'[^\x00-\x7F]+', ' ', name)
    printable = set(string.printable)
    name = ''.join(filter(lambda x: x in printable, name)).strip()
    name = " ".join(re.sub(r'\s([?.!,"](?:\s|$))', r'\1', name).split())
    for join_number in JOIN_NUMBERS.keys():
        if_present = name.find(join_number)
        if if_present != -1:
            name = name.replace(join_number, str(JOIN_NUMBERS[join_number]), 1)
    return name


def unit_conversion(unit, qty):
    if unit == "A pinch":
        qty = 1
        unit = "pinch"
    # Unit conversion fluid ounce ,ounce to ml
    if unit == "fluid_ounce":
        unit = "milliliter"
        try:
            qty = str(round(float(qty) * 30, 2))
        except:
            if qty is not None and qty != "":
                temp_qty = qty.split("-")
                try:
                    temp_qty[0] = str(round(int(temp_qty[0]) * 30, 2))
                    temp_qty[1] = str(round(int(temp_qty[1]) * 30, 2))
                    qty = "-".join(temp_qty)
                except:
                    print("quantity has errors")
    # unit conversion cl to ml
    if unit == "centiliter":
        unit = "milliliter"
        try:
            qty = str(round(float(qty) * 10, 2))
        except:
            if qty is not None and qty != "":
                temp_qty = qty.split("-")
                try:
                    temp_qty[0] = str(round(int(temp_qty[0]) * 10, 2))
                    temp_qty[1] = str(round(int(temp_qty[1]) * 10, 2))
                    qty = "-".join(temp_qty)
                except:
                    print("quantity has errors")
    # if qty is present ,unit will not be As required
    if unit == "As required" and qty is not None:
        unit = None
    return unit, qty


def parse_ingredients_v1(ingredients):
    output_list = []
    ingredients_list = []
    for one_section in ingredients:
        for i in one_section['ingredients']:
            name = i.replace("&frac34;", "3/4")
            name = name.replace("&frac12;", "1/2")
            name = name.replace("&frac14;", "1/4")
            # for Hebbers kitchen errors
            # name = name[0:len(name) // 2]
            one_ingr = {}
            # try:
            # replace bracket and its contents
            # replace bracket and its contents
            name = ingredient_preprocess(name)
            og_name = name
            qty, name = parse_qty(name)
            unit, unit_index, og_unit = parse_unit(og_name)
            name, qty = match_unit_qty(qty, unit_index, og_name, og_unit)
            unit, qty = unit_conversion(unit, qty)
            name = cleaned_name(name)
            # except Exception as e:
            #     print("### Error ", e, i)
            #     name = i
            #     unit = None
            #     qty = None
            skip = 0
            # Join quantity of duplicate ingredients
            if name in ingredients_list:
                for repeat_ingr in output_list:
                    if repeat_ingr["ingredient"] == name:
                        if repeat_ingr["unit"] == unit:
                            try:
                                new_qty = round(
                                    float(repeat_ingr["quantity"] if repeat_ingr["quantity"] else 0) + float(
                                        qty if qty else 0), 2)
                                repeat_ingr["quantity"] = str(new_qty if new_qty else None)
                                skip = 1
                            except ValueError:
                                print("Cannot add non-float values", i, name, qty, unit)
            else:
                ingredients_list.append(name)

            if not skip:
                one_ingr["ingredient"] = name.capitalize()
                one_ingr["unit"] = unit
                one_ingr["quantity"] = qty
                if name.strip() != "":
                    output_list.append(one_ingr)
    return output_list


def parse_ingredients_v2(ingredients):
    output_list = []
    ingredients_list = []
    for i in ingredients:
        name = i.replace("&frac34;", "3/4")
        name = name.replace("&frac12;", "1/2")
        name = name.replace("&frac14;", "1/4")
        # for Hebbers kitchen errors
        # name = name[0:len(name) // 2]
        one_ingr = {}
        # try:
        # replace bracket and its contents
        # replace bracket and its contents
        name = ingredient_preprocess(name)
        og_name = name
        qty, name = parse_qty(name)
        unit, unit_index, og_unit = parse_unit(og_name)
        name, qty = match_unit_qty(qty, unit_index, og_name, og_unit)
        unit, qty = unit_conversion(unit, qty)
        name = cleaned_name(name)
        # except Exception as e:
        #     print("### Error ", e, i)
        #     name = i
        #     unit = None
        #     qty = None
        skip = 0
        # Join quantity of duplicate ingredients
        if name in ingredients_list:
            for repeat_ingr in output_list:
                if repeat_ingr["ingredient"].lower() == name.lower():
                    if repeat_ingr["unit"] == unit:
                        try:
                            new_qty = round(float(repeat_ingr["quantity"] if repeat_ingr["quantity"] else 0) + float(
                                qty if qty else 0), 2)
                            repeat_ingr["quantity"] = str(new_qty if new_qty else None)
                            skip = 1
                        except ValueError:
                            print("Cannot add non-float values", i, name, qty, unit)
        else:
            ingredients_list.append(name)

        if not skip:
            one_ingr["ingredient"] = name.capitalize()
            one_ingr["unit"] = unit
            one_ingr["quantity"] = qty
            if name.strip() != "":
                output_list.append(one_ingr)
        print(i)
        print(one_ingr)
    return output_list


if __name__ == '__main__':
    import time

    # for sample testing
    input2 = ["1  onions",
              '1 ¼ cups all-purpose flour', '1/4 cup\npowdered sugar', '1/8 teaspoon salt',
              '1  stick ((4 oz. unsalted butter, slightly softened))',
              '1 cup mascarpone cheese ((about 8 ounces))',
              '1/3 cup chilled heavy cream', '1/3 cup sugar', '1 cup raspberries',
              '1 cup blackberries',
              '2 tablespoons apricot jam', '2 tablespoons Grand Marnier ((optional))',
              '5-7 lbs beef shoulder or brisket', "Icing sugar teaspoon.",
              '""+ 1 cup rice', '¼ Tbsp dried oregano', '1 cup\n fresh or frozen cranberries',
              '1 Tbsp granulated garlic or garlic powder',
              '1 Tbsp onion powder',
              '1 Tbsp dried thyme', '1 Tbsp turmeric', '2 tsp ground ginger',
              '1 Tbsp salt, divided', '1 medium bunch cilantro, roughly chopped',
              '1 medium red onion, roughly cut',
              '1 head garlic, peeled and cloves smashed',
              '2 sticks cinnamon (Mexican cinnamon, preferred)', '5 bay leaves',
              '3 1/2 Tbsp fish sauce', '1 Tbsp blackstrap molasses', 'Juice of 4 limes',
              '1 1/2 cup apple cider vinegar',
              '4 cups beef broth (enough to cover beef shoulder/brisket)',
              '8 or 10 cup rice',
              '½ cup -split green moong dal', '¼ cup -chana dal', '¼ cup -arhar/ tuvar dal',
              'Salt', 'Turmeric', 'Water', 'Ingredients for Tadka',
              '3 tbsp - ghee/ Clarified butter', '1tsp - cumin seeds/ Jeera',
              '1tsp - mustard/ Rai', '4-5 nos - Cloves/ Laung',
              '1 nos - bay leaf / Tej Patta', '2 nos - Dry red chillies',
              '1 cup - fine chopped onions', '1 cup - finely chopped tomatoes',
              '1 tsp -grated ginger', '1 tsp -grated garlic', 'Salt', '½ tsp -turmeric',
              '1 tsp -red chilli powder', '1 tsp -coriander powder', '¼ tsp -garam masala',
              '1 tsp -kasuri methi', '1.5 tbsp -lemon juice', '2tbsp -coriander leaves',
              'Chana Daal – 3/4 cup', 'Yellow Split Moong Daal – handful',
              '1¼ cups all-purpose flour',
              '½ - ¾ cup condensed milk ((depending on your preferences for sweetness))',
              "Red chilli powder as per taste", "5 + 1 a",
              "1-2 fl. oz. rum",
              "1/2 fl oz rum",
              "aloo", "2 dash Angostura Aromatic Bitters", 'Ã\x83Â\x82Ã\x82Â½ oz Vodka',
              "1/2 CUP tamarind JUICE",
              'tsp\xa0 oil2\xa0 tsp\xa0 oil', "two half potatos", "1 spoons. rice",
              "1 ÃÂÃÂ½ ounces Calvados",
              "200g / 1cup rice", "1 potato 100 g", ".66 potato",
              "as per your taste sugar 1  ", "3 and half pint canning jars with lids and rings",
              "leg adpiece 1 ", "8 x 5mm slices Helga's black bread",
              "1 1/2 cups rolled oats, plus more for topping",
              "8 half-pint wide-mouth canning jars or ramekins OR a 9 x 9 baking dish (or 9-inch round pie pan)",
              "1 1/2\xa0cups rolled oats, plus more for topping", "4 half-pint canning jars or ramekins", "a 1 x qhc",
              '1-1 1/2g good-quality bought christmas pudding', "8 no. oninons", "water    1 and 1 1/2   cup",
              "10 large or 750 grams or 5 ½ cups Carrot", " '3 x 250-300g marron,  split and cleaned. '",
              "3 x 125g Uncle Ben’s® Mexican Rice and Beans Cups", '1 ½ to 3 tablespoons honey, to taste',
              "¾ to 1 cup cooked quinoa (see step 1 below)",
              '⅓ cup homemade muesli, or ⅓ cup old-fashioned oats plus ¼ teaspoon ground cinnamon',
              "2.5 to 3.5 kg rice", "1 1/2 cups/225 grams all-purpose flour (sifted)", "1 rice as per taste",
              '2 8-ounce/225g pork tenderloins', '2 1 lb./450 g trout']
    # input2 =['\n1\ngallon\nhome-brewed kombucha\n', '\n2\ntablespoons\nfresh ginger\npeeled and finely grated\n', '\n1\ncup\napple juice\n', '\n1\nteaspoon\nground cinnamon\n', '\n8\nDried apple rings *\none apple ring per bottle\n']
    # input2 = ['2 fluid ounces sake', '1 fluid ounce peach schnapps', '2 fluid ounces orange juice',
    #           '2 fluid ounces 100% cranberry juice', 'ice cubes']
    # input2 = [' 3 to 3 1/2 cups all-purpose flour',
    #           ' 2 tsp instant yeast or one envelope, which is equivalent to 2 1/4 teaspoons', ' 1/4 cup sugar',
    #           ' 1 tsp salt', ' 2 eggs plus 1 egg separated (saving the white for egg wash)',
    #           ' 1/4 cup 1/2 stick unsalted butter softened',
    #           ' 1/4 cup boiling water plus 1/4 cup room temperature water', ' 1 tsp poppy or sesame seeds optional']
    # input2 = ['150g Three Threes Old Style pickled onions, drained, coarsely chopped',
    #           '3 (about 315g) egg tomatoes, coarsely chopped',
    #           '1 firm golden delicious apple, cored, finely coarsely chopped', '2 teaspoons brown sugar',
    #           '1 garlic clove, crushed', '1 tablespoon finely grated orange rind', '60ml (1/4 cup) fresh orange juice',
    #           '1 egg', '2 tablespoons water', 'Plain flour, to dust', '180g (1 1/2 cups) dried (packaged) breadcrumbs',
    #           '4 (about 400g) small fish fillets (such as whiting or bream)', 'Olive oil spray',
    #           '1x100g pkt baby Asian salad leaves', "chilli as per taste", "5-6 tomato"]
    # input2 = ['2 15-ounce cans of garbanzo beans, rinsed and drained with liquid reserved', '1/4 cup tahini',
    #           '1 1/2 teaspoon curry powder', '1 handful cilantro leaves', '2 cloves garlic,minced', 'Juice of 1 lemon',
    #           '1/2 teaspoon salt', "15-kg rice", "1 1/2 kg rice", "8 No. oninons",
    #           "1 medium or ¾ cup Mangoes (chopped)",
    #           "1-2 scoops + 1 scoop  Ice cream (Vanilla or Mango)", "4 no.  Bati", "1 ½ to 2 tablespoons Sugar",
    #           "6 stalks or 2 cups Spring onion (green onion or scallion) (chopped)", "2.3kg rice",
    #           '2 x 2.3kg Coles RSPCA Approved Extra Large Whole Chickens', "4 egg whites 140g",
    #           "1/4 + 1/8 teaspoon kosher salt",
    #           "1+6 ascn", "1 and 3 sdc", "0.2 +0.3 sc"]
    # input2 = ["1 cup or 200g rice", "1 x 300g of icecream"]
    start = time.time()
    # parse_ingredients_v2(input2)
    import pandas as pd

    #
    # df = pd.read_csv("/home/webwerks/Downloads/Cookieandkate_cleaned.csv", usecols=["recipe_ingredient_list"])
    # df["abcd"] = df['recipe_ingredient_list'].apply(lambda x: parse_ingredients_v1(eval(x)))
    # df.to_csv("output_ingredinet.csv", index=False)
    parse_ingredients_v2(input2)
    # for i in input2:
    #     print(parse_qty(i), i)
    #     print(parse_unit(i, i), i)
    # end = time.time()
    # print(start - end)
