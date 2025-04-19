import logging
import re
import uuid

import rstr

from xmlgenerator.randomization import Randomizer

__all__ = ['Substitutor']

_pattern = re.compile(pattern=r'\{\{\s*(?:(?P<function>\S*?)(?:\(\s*(?P<argument>[^)]*)\s*\))?\s*(?:\|\s*(?P<modifier>.*?))?)?\s*}}')

logger = logging.getLogger(__name__)

class Substitutor:
    def __init__(self, randomizer: Randomizer):
        fake = randomizer.fake
        self.randomizer = randomizer
        self._local_context = {}
        self._global_context = {}
        self.providers_dict = {
            # Функции локального контекста
            'source_filename': lambda: self._local_context["source_filename"],
            'source_extracted': lambda: self._local_context["source_extracted"],
            'output_filename': lambda: self.get_output_filename(),

            'uuid': lambda: str(uuid.uuid4()),
            'regex': lambda a: rstr.xeger(a),
            'any': self._rand_any,
            'number': self._rand_int,
            'date': self._rand_date,

            'last_name': fake.last_name_male,
            'first_name': fake.first_name_male,
            'middle_name': fake.middle_name_male,
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

    def _rand_any(self, a):
        args = str(a).split(sep=",")
        value = self.randomizer.rnd.choice(args)
        value = value.strip(' ').strip("'").strip('"')
        return value

    def _rand_int(self, a):
        args = str(a).split(sep=",")
        return str(self.randomizer.rnd.randint(int(args[0]), int(args[1])))

    def _rand_date(self, a):
        args = str(a).split(sep=",")
        date_from = args[0].strip(' ').strip("'").strip('"')
        date_until = args[1].strip(' ').strip("'").strip('"')
        random_date = self.randomizer.random_datetime(date_from, date_until)
        return random_date.strftime('%Y%m%d') # TODO externalize pattern

    def reset_context(self, xsd_filename, config_local):
        self._local_context.clear()
        self._local_context["source_filename"] = xsd_filename

        source_filename = config_local.source_filename
        matches = re.search(source_filename, xsd_filename).groupdict()
        source_extracted = matches['extracted']
        self._local_context["source_extracted"] = source_extracted

        output_filename = config_local.output_filename
        resolved_value = self._process_expression(output_filename)
        self._local_context['output_filename'] = resolved_value

        logger.debug('local_context reset')
        logger.debug('local_context["source_filename"]  = %s', xsd_filename)
        logger.debug('local_context["source_extracted"] = %s (extracted with regexp %s)', source_extracted, source_filename)
        logger.debug('local_context["output_filename"]  = %s', resolved_value)

    def get_output_filename(self):
        return self._local_context.get("output_filename")

    def substitute_value(self, target_name, items):
        for target_name_pattern, expression in items:
            if re.search(target_name_pattern, target_name, re.IGNORECASE):
                if expression:
                    result_value = self._process_expression(expression)
                    return True, result_value
                else:
                    return False, None
        return False, None

    def _process_expression(self, expression):
        logger.debug('processing expression: %s', expression)
        global_context = self._global_context
        local_context = self._local_context
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

            provider_func = lambda: func_lambda() if not func_args else func_lambda(func_args)

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

        logger.debug('expression resolved to value: %s', result_value)
        return result_value
