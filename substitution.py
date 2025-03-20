import re
import uuid
from typing import Dict, Callable

from randomization import Randomizer

__all__ = ['Substitutor']

_pattern = re.compile(pattern=r'\{\{\s*(?:(?P<function>.*?)\s*(?:\|\s*(?P<modifier>.*?))?)?\s*\}\}')


def _init_providers(randomizer: Randomizer) -> Dict[str, Callable[[], str]]:
    fake = randomizer.fake
    return {
        "file_name": lambda: randomizer._id_file,
        'uuid': lambda: str(uuid.uuid4()),
        "last_name": fake.last_name_male,
        "first_name": fake.first_name_male,
        "middle_name": fake.middle_name_male,
        'address_text': fake.address,
        'administrative_unit': fake.administrative_unit,
        'house_number': fake.building_number,
        'city_name': fake.city_name,
        'postcode': fake.postcode,
        'company_name': fake.company,
        'bank_name': fake.bank,
        'phone_number': fake.phone_number,
        'inn_fl': fake.individuals_inn,
        'inn_ul': fake.businesses_inn,
        'ogrn_ip': fake.individuals_ogrn,
        'ogrn_fl': fake.businesses_ogrn,
        'kpp': fake.kpp,
        'snils_formatted': randomizer.snils_formatted,
    }


class Substitutor:
    def __init__(self, randomizer: Randomizer):
        self.randomizer = randomizer
        self.providers_dict = _init_providers(randomizer)

    def substitute_value(self, target_name, items):
        global_context = self.randomizer._global_context
        local_context = self.randomizer._local_context
        for target_name_pattern, expression in items:
            if re.search(target_name_pattern, target_name, re.IGNORECASE):
                result_value: str = expression
                span_to_replacement = {}
                matches = _pattern.finditer(expression)
                for match in matches:
                    func_name = match[1]
                    modifier = match[2]
                    provider_func = self.providers_dict[func_name]
                    if not provider_func:
                        raise RuntimeError(f"Unknown function {func_name}")
                    match modifier:
                        case None:
                            resolved_value = provider_func()
                        case 'global':
                            resolved_value = global_context.get(func_name) or provider_func()
                            global_context[func_name] = resolved_value
                        case 'local':
                            resolved_value = local_context.get(func_name) or provider_func()
                            local_context[func_name] = resolved_value
                        case _:
                            raise RuntimeError(f"Unknown modifier {modifier}")

                    span_to_replacement[match.span()] = resolved_value

                for span, replacement in reversed(list(span_to_replacement.items())):
                    result_value = result_value[:span[0]] + replacement + result_value[span[1]:]

                return True, result_value
        return False, None

    def make_filename(self, xsd_name):
        matches = re.findall("^((ON|DP)_[A-Z0-9]*)_.*", xsd_name)
        file_id_prefix = matches[0][0]
        return self.randomizer.id_file(file_id_prefix)
