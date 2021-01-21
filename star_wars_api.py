import json, requests

ENDPOINT = 'https://swapi.co/api'

PEOPLE_KEYS = ('url', 'name', 'height', 'mass', 'hair_color', 'skin_color', 'eye_color', 'birth_year', 'gender', 'homeworld', 'species')
PLANET_KEYS = ('url', 'name', 'rotation_period', 'orbital_period', 'diameter', 'climate', 'gravity', 'terrain', 'surface_water', 'population')
PLANET_HOTH_KEYS = ('url', 'name', 'system_position', 'natural_satellites', 'rotation_period', 'orbital_period', 'diameter', 'climate', 'gravity', 'terrain', 'surface_water', 'population', 'indigenous_life_forms')
STARSHIP_KEYS = ('url', 'starship_class', 'name', 'model', 'manufacturer', 'length', 'width', 'max_atmosphering_speed', 'hyperdrive_rating', 'MGLT', 'crew', 'passengers', 'cargo_capacity', 'consumables', 'armament')
SPECIES_KEYS = ('url', 'name', 'classification', 'designation', 'average_height', 'skin_colors', 'hair_colors', 'eye_colors', 'average_lifespan', 'language')
VEHICLE_KEYS = ('url', 'vehicle_class', 'name', 'model', 'manufacturer', 'length', 'max_atmosphering_speed', 'crew', 'passengers', 'cargo_capacity', 'consumables', 'armament')


def assign_crew(starship, crew):
    '''This function assigns crew members to a starship. The function defines two parameters, 
    starship and crew, both of them being dictionary. The function returns an updated starship with one or more 
    new crew member in key-value pairs.

    Parameters:
        starship (dict): Dicitonary of starship.
        crew (dict): Crew dictionary.
        
    Returns:
        dict: Updated Starship and new crew member as one or more key-value pairs.
    '''
    starship.update(crew)
    return starship


def clean_data(entity):
    '''This function converts dictionary string values to values of the type float, int, 
    list, or, in some cases, None. The function defines a single parameter 'entity' which is a dictionary. The 
    function evaluates each key-value pair and passes them through the if-elif-else conditional statements, 
    membership operators, and calls to other functions in order to convert them to the above mentioned value types.
    Finally, the function will return a dictionary with 'cleaned' values.

    Parameters: 
        entity (dict): Takes up the data of the type (dict) and converts it to different type as assigned.

    Returns:
        dict: Cleaned values after converting them to desired type.

    '''
    float_props = ('gravity', 'length', 'hyperdrive_rating')
    int_props = ('rotation_period', 'orbital_period', 'diameter', 'surface_water', 'population',
             'height', 'mass', 'average_height', 'average_lifespan', 'max_atmosphering_speed',
             'MGLT', 'crew', 'passengers', 'cargo_capacity')
    list_props = ('hair_color', 'skin_color', 'climate', 'terrain', 'hair_colors', 'skin_colors', 'eye_colors')

    cleaned = {}
    for key,value in entity.items():
        if type(value) == str and is_unknown(value):
            cleaned[key] = None
        elif key in float_props:
            if key == 'gravity':
                value = value.replace('standard','').strip()
            cleaned[key] = convert_string_to_float(value)
        elif key in int_props:
            cleaned[key] = convert_string_to_int(value)
        elif key in list_props:
            value = value.strip()
            cleaned[key] = convert_string_to_list(value, delimiter=', ')
        elif key == 'homeworld':
                hom = get_swapi_resource(value)
                new_hom = filter_data(hom, PLANET_KEYS)
                cleaned[key] = clean_data(new_hom)
        elif key == 'species':
                spec = get_swapi_resource(value[0])
                new_spec = filter_data(spec, SPECIES_KEYS)
                cleaned[key] = [clean_data(new_spec)]
        else:
            cleaned[key] = value
    return cleaned


def combine_data(default_data, override_data):
    '''
    This function creates a shallow copy of the default dictionary and then updates the copy 
    with key-value pairs from the 'override' dictionary. The function defines two parameters, 
    default_data and override_data both of them being dictionary.

    Parameters:
        default_data (dict): Default dictionary.
        override_data (dict): Dicitonary that overwrites values in default dicitonary.

    Returns:
        dict: Dictionary with new key-value pairs.The resultant dictionary comprises of the key-value pairs 
        of both the default dictionary and the override dictionary, with override 
        values replacing default values on matching keys.

    '''
    combined_data = default_data.copy()
    combined_data.update(override_data)
    return combined_data


def convert_string_to_float(value):
    '''
    This function attempts to convert a string to a float value. The function defines a 
    single parameter value which is a string.

    Parameters:
        value (str): String value gets converted to a float.

    Returns: 
        float: Floating point value if successful and otherwise retuens the unchanged value 

    '''
    try:
        return float(value)
    except ValueError:
        return value


def convert_string_to_int(value):
    '''
    This function attempts to convert a string to an integer value. The function defines a 
    single parameter value which is a string.

    Parameters:
        value (str): String gets converted to a integer.

    Returns:
        int: Integer value if successful and otherwise retuens the unchanged value 

    '''
    
    try:
       return int(value)
    except ValueError:
        return value


def convert_string_to_list(value, delimiter = ','):
    '''This function converts a string of delimited text values to a list. The function defines two 
    parameters, value and an optional delimiter both of which are of the type string. The function will split the 
    string passed at the stated delimiter and return the result list.

    Parameters:
        value (str): String to be splitted.
        delimiter (str): String where passed string is to be splitted.

    Returns:
        list: List of the splitted string elements.
    '''
    some_value = value.split(delimiter)  
    return some_value 


def filter_data(data, filter_keys):
    '''
    This function applies a key-name filter to a dictionary in order to return an ordered subset 
    of key-value pairs. The function defines two parameters, data which is a dictionary and filter_keys which is a tuple. The 
    function returns a filtered collection of key-value pairs.

    Parameters:
        data (dict): The original dicitonary.
        filter_keys (tuple): Tuples of the keys which are to be filtered fromt he original dictionary

    Returns:
        dict: Filtered collection of key-value pairs from original dicitonary.
    '''
    new_dict = {}
    for key in filter_keys:
        if key in data.keys():
            new_dict[key] = data[key]
    return new_dict


def get_swapi_resource(url, params=None):
    '''
    This function calls an HTTP via GET request to the SWAPI url to return a 
    representation of a resource. The function contains two parameters, the resource url and 
    an optional params which is a query string of key:value pairs that can be provided as search terms 
    (e.g., {'search': 'yoda'}). SWAPI data is serialized as JSON. 

    Parameters:
        url (str): It is the resource url
        params (dict): Query string of key:value pairs that can be searched

    Returns: 
        dict: Result contains the resource(s) matched by the search query terms. The get_swapi_resource() function 
        decodes the response using the .json() method and returns a dictionary.
    '''
    if params:
        response = requests.get(url, params=params).json()
    else:
        response = requests.get(url).json()
    return response    


def is_unknown(value):
    '''
    This function applies a case-insensitive truth value test for string values that are equal to unknown 
    or n/a. The function defines a single parameter value which is of the type string. 

    Parameters:
        Value (str): String value to test the truth value criteria.

    Returns:
        bool: Returns True if a match is obtained otherwise False.
    '''
    if value.lower().strip() == 'unknown':
           return True
    elif value.lower().strip() == 'n/a':
        return True
    else:
        return False    


def read_json(filepath):
    
    """Given a valid filepath reads a JSON document and returns a dictionary.

    Parameters:
        filepath (str): path to file.

    Returns:
        dict: dictionary representations of the decoded JSON document.
    """

    with open(filepath, 'r', encoding='utf-8') as read_file:
        data = json.load(read_file)
    return data


def write_json(filepath, data):
    '''
    This function writes SWAPI data to a target JSON document file. The function defines two parameters, filepath which is a string
    and the data which is a dictionary that is to be written to the JSON file. The function processes various combination of SWAPI data 
    and filepath provided to it as arguments. The built-in open() function has the encoding parameter set to utf-8. 
    When calling json.dump() the parameter ensure_ascii is set to False and the indent parameter to 2.

    Parameters:
        filepath (str): The JSON file that is to be written.
        data (dict): The data that is to be written to the file.

    Returns: 
        dict: The function returns dictionary represented in JSON format.

    '''
    with open(filepath, 'w', encoding= 'utf-8') as write_file:
        json.dump(data, write_file, ensure_ascii= False, indent= 2)

def main():
    """
    Entry point. This program will interact with local file assets and the Star Wars
    API to create two data files required by Rebel Alliance Intelligence.

    - A JSON file comprising a list of likely uninhabited planets where a new rebel base could be
      situated if Imperial forces discover the location of Echo Base.

    - A JSON file of Echo Base information including an evacuation plan of base personnel
      along with passenger assignments for Princess Leia, the communications droid C-3PO aboard
      the transport Bright Hope escorted by two X-wing starfighters piloted by Luke Skywalker
      (with astromech droid R2-D2) and Wedge Antilles (with astromech droid R5-D4).

    Parameters:
        None

    Returns:
        None
    """

    file_ = 'swapi_planets-v1p0.json'
    main_ = read_json(file_)
    uninhabited_planets = []
    for pop in main_:
        num = pop.get('population')
        if is_unknown(num) == True:
            neat = filter_data(pop, PLANET_KEYS)
            uninhabited_planets.append(clean_data(neat))
            write_json('swapi_planets_uninhabited-v1p1.json', uninhabited_planets)

    echo_base = read_json('swapi_echo_base-v1p0.json')

    swapi_hoth_url = f"{ENDPOINT}/planets/"
    swapi_hoth = get_swapi_resource(swapi_hoth_url, {'search': 'hoth'})['results'][0]
    echo_base_hoth = echo_base['location']['planet']
    hoth = combine_data(echo_base_hoth, swapi_hoth)
    hoth = filter_data(hoth, PLANET_HOTH_KEYS)
    hoth = clean_data(hoth)
    echo_base['location']['planet'] = hoth

    echo_base_commander = echo_base['garrison']['commander']
    echo_base_commander = clean_data(echo_base_commander)
    echo_base['garrison']['commander'] = echo_base_commander

    echo_base_dash_rendar = echo_base['visiting_starships']['freighters'][1]['pilot']
    echo_base_dash_rendar = clean_data(echo_base_dash_rendar)
    echo_base['visiting_starships']['freighters'][1]['pilot'] = echo_base_dash_rendar

    swapi_vehicles_url = f"{ENDPOINT}/vehicles/"
    swapi_snowspeeder = get_swapi_resource(swapi_vehicles_url, {'search': 'snowspeeder'})['results'][0]
    echo_base_snowspeeder = echo_base['vehicle_assets']['snowspeeders'][0]['type']
    snowspeeder = combine_data(echo_base_snowspeeder, swapi_snowspeeder)
    snowspeeder = filter_data(snowspeeder, VEHICLE_KEYS)
    snowspeeder = clean_data(snowspeeder)
    echo_base['vehicle_assets']['snowspeeders'][0]['type'] = snowspeeder

    swapi_starships_url = f"{ENDPOINT}/starships/"
    swapi_t_65 = get_swapi_resource(swapi_starships_url, {'search': 't-65 x-wing'})['results'][0]
    echo_base_t_65 = echo_base['starship_assets']['starfighters'][0]['type']
    t_65 = combine_data(echo_base_t_65, swapi_t_65)
    t_65 = filter_data(t_65, STARSHIP_KEYS)
    t_65 = clean_data(t_65)
    echo_base['starship_assets']['starfighters'][0]['type'] = t_65

    swapi_gr_75 = get_swapi_resource(swapi_starships_url, {'search': 'gr-75 medium transport'})['results'][0]
    echo_base_gr_75 = echo_base['starship_assets']['transports'][0]['type']
    gr_75 = combine_data(echo_base_gr_75, swapi_gr_75)
    gr_75 = filter_data(gr_75, STARSHIP_KEYS)
    gr_75 = clean_data(gr_75)
    echo_base['starship_assets']['transports'][0]['type'] = gr_75

    swapi_millennium_falcon = get_swapi_resource(swapi_starships_url, {'search': 'millennium falcon'})['results'][0]
    echo_base_millennium_falcon = echo_base['visiting_starships']['freighters'][0]
    m_falcon = combine_data(echo_base_millennium_falcon, swapi_millennium_falcon)
    m_falcon = filter_data(m_falcon, STARSHIP_KEYS)
    m_falcon = clean_data(m_falcon)
    echo_base['visiting_starships']['freighters'][0] = m_falcon

    swapi_people_url = f"{ENDPOINT}/people/"
    han = get_swapi_resource(swapi_people_url, {'search': 'han solo'})['results'][0]
    han = filter_data(han, PEOPLE_KEYS)
    han = clean_data(han)
    chewba = get_swapi_resource(swapi_people_url, {'search': 'chewbacca'})['results'][0]
    chewba = filter_data(chewba, PEOPLE_KEYS)
    chewba = clean_data(chewba)
    m_falcon = assign_crew(m_falcon, {'pilot': han, 'copilot': chewba})
    echo_base['visiting_starships']['freighters'][0] = m_falcon

    evac_plan = echo_base['evacuation_plan']
    max_base_personnel = 0
    personnel_dict = echo_base['garrison']['personnel']
    for value in personnel_dict.values():
        max_base_personnel += value
    evac_plan['max_base_personnel'] = max_base_personnel
    max_available_transports = echo_base['starship_assets']['transports'][0]['num_available']
    evac_plan['max_available_transports'] = max_available_transports
    passenger_overload_multiplier = evac_plan['passenger_overload_multiplier']
    standard_passenger_carrying_capacity = echo_base['starship_assets']['transports'][0]['type']['passengers']
    evac_plan['max_passenger_overload_capacity'] = max_available_transports * passenger_overload_multiplier * standard_passenger_carrying_capacity
    
    evac_transport = gr_75.copy()

    evac_transport['name'] = 'Bright Hope'

    write_json('swapi_echo_base-v1p1.json', echo_base)

    evac_transport['passenger_manifest'] = []
    leia = get_swapi_resource(swapi_people_url, {'search': 'leia organa'})['results'][0]
    leia = filter_data(leia, PEOPLE_KEYS)
    leia = clean_data(leia)
    c3po = get_swapi_resource(swapi_people_url, {'search': 'C-3PO'})['results'][0]
    c3po = filter_data(c3po, PEOPLE_KEYS)
    c3po = clean_data(c3po)
    evac_transport['passenger_manifest'] = [leia, c3po]

    evac_transport['escorts'] = []
    luke_x_wing = t_65.copy()
    wedge_x_wing = t_65.copy()
    luke = get_swapi_resource(swapi_people_url, {'search': 'luke skywalker'})['results'][0]
    luke = filter_data(luke, PEOPLE_KEYS)
    luke = clean_data(luke)
    r2d2 = get_swapi_resource(swapi_people_url, {'search': 'r2-d2'})['results'][0]
    r2d2 = filter_data(r2d2, PEOPLE_KEYS)
    r2d2 = clean_data(r2d2)
    luke_x_wing = assign_crew(luke_x_wing, {'pilot': luke, 'astromech_droid': r2d2})
    evac_transport['escorts'].append(luke_x_wing)

    wedge = get_swapi_resource(swapi_people_url, {'search': 'wedge antilles'})['results'][0]
    wedge = filter_data(wedge, PEOPLE_KEYS)
    wedge = clean_data(wedge)
    r5d4 = get_swapi_resource(swapi_people_url, {'search': 'r5-d4'})['results'][0]
    r5d4 = filter_data(r5d4, PEOPLE_KEYS)
    r5d4 = clean_data(r5d4)
    wedge_x_wing = assign_crew(wedge_x_wing, {'pilot': wedge, 'astromech_droid': r5d4})
    evac_transport['escorts'].append(wedge_x_wing)


    evac_plan['transport_assignments'] = [evac_transport]

    echo_base['evacuation_plan'] = evac_plan

    filename = 'swapi_echo_base-v1p1.json'
    write_json(filename, echo_base)

if __name__ == '__main__':
    main()

