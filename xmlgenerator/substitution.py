import re
import uuid

import rstr

from xmlgenerator.randomization import Randomizer

__all__ = ['Substitutor']

_pattern = re.compile(pattern=r'\{\{\s*(?:(?P<function>\S*?)(?:\(\s*(?P<argument>[^)]*)\s*\))?\s*(?:\|\s*(?P<modifier>.*?))?)?\s*}}')

def _rand_int(randomizer, a):
    args = str(a).split(sep=",")
    return str(randomizer.rnd.randint(int(args[0]), int(args[1])))

class Substitutor:
    def __init__(self, randomizer: Randomizer):
        fake = randomizer.fake
        self.randomizer = randomizer
        self._local_context = {}
        self._global_context = {}
        self.providers_dict = {
            # локальные функции
            "source_extracted": lambda: self._local_context["source_filename"], # TODO
            "source_filename": lambda: self._local_context["source_filename"],
            "output_filename": lambda: self.get_output_filename(),

            'uuid': lambda: str(uuid.uuid4()),
            "regex": lambda a: rstr.xeger(a),
            "number": lambda a: _rand_int(randomizer, a),

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

    def reset_context(self):
        self._local_context.clear()

    def substitute_value(self, target_name, items):
        global_context = self._global_context
        local_context = self._local_context
        for target_name_pattern, expression in items:
            if re.search(target_name_pattern, target_name, re.IGNORECASE):
                result_value: str = expression
                span_to_replacement = {}
                matches = _pattern.finditer(expression)
                for match in matches:
                    func_name = match[1]
                    func_args = match[2]
                    func_mod = match[3]
                    func_lambda = self.providers_dict[func_name]
                    if not func_lambda:
                        raise RuntimeError(f"Unknown function {func_name}")

                    provider_func = lambda : func_lambda() if not func_args else func_lambda(func_args)

                    match func_mod:
                        case None:
                            resolved_value = provider_func()
                        case 'global':
                            resolved_value = global_context.get(func_name) or provider_func()
                            global_context[func_name] = resolved_value
                        case 'local':
                            resolved_value = local_context.get(func_name) or provider_func()
                            local_context[func_name] = resolved_value
                        case _:
                            raise RuntimeError(f"Unknown modifier: {func_mod}")

                    span_to_replacement[match.span()] = resolved_value

                for span, replacement in reversed(list(span_to_replacement.items())):
                    result_value = result_value[:span[0]] + replacement + result_value[span[1]:]

                return True, result_value
        return False, None

    def get_output_filename(self, xsd_name=None):
        resolved_value = self._local_context.get("output_filename")
        if not resolved_value and xsd_name:
            matches = re.findall("^((ON|DP)_[A-Z0-9]*)_.*", xsd_name)
            file_id_prefix = matches[0][0]
            resolved_value = self.randomizer.id_file(file_id_prefix)
            self._local_context["source_filename"] = xsd_name
            self._local_context["output_filename"] = resolved_value
        return resolved_value
