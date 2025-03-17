import re
from typing import Dict, Callable

from generate_static import id_file_str, config
from util_random import fake, snils_formatted

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


def get_value_override(target_name):
    for pattern, substitution in config.global_.value_override.items():
        if re.search(pattern, target_name, re.IGNORECASE):
            rnd_func_matches = re.findall(r"\$rnd\('(.*)'\)", substitution, re.IGNORECASE)
            if rnd_func_matches:
                rnd_function = rnd_functions[rnd_func_matches[0]]
                return True, rnd_function()
            else:
                return True, substitution
    return False, None
