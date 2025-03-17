import re
from typing import Dict, Callable

from randomization import fake, snils_formatted, id_file

global id_file_str

rnd_functions: Dict[str, Callable[[], str]] = {
    "фамилия": fake.last_name_male,
    "имя": fake.first_name_male,
    "отчество": fake.middle_name_male,
    'адрес': fake.address,
    'район': fake.administrative_unit,
    'номер_дома': fake.building_number,
    'город': fake.city_name,
    'почтовый_индекс': fake.postcode,
    'компания': fake.company,
    'банк': fake.bank,
    'номер_телефона': fake.phone_number,
    'инн_фл': fake.individuals_inn,
    'инн_юл': fake.businesses_inn,
    'огрн_ип': fake.individuals_ogrn,
    'огрн_фл': fake.businesses_ogrn,
    'кпп': fake.kpp,
    'снилс': snils_formatted,
    "фнс__ид_файл" : lambda : id_file_str
}


def init_id_file(xsd_name):
    matches = re.findall("^((ON|DP)_[A-Z0-9]*)_.*", xsd_name)
    file_id_prefix = matches[0][0]
    global id_file_str
    id_file_str = id_file(file_id_prefix)
    return id_file_str


def get_value_override(target_name, items):
    for pattern, substitution in items:
        if re.search(pattern, target_name, re.IGNORECASE):
            rnd_func_matches = re.findall(r"\$rnd\('(.*)'\)", substitution, re.IGNORECASE)
            if rnd_func_matches:
                rnd_function = rnd_functions[rnd_func_matches[0]]
                return True, rnd_function()
            else:
                return True, substitution
    return False, None
