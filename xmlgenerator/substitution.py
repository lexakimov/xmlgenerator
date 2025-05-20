import logging
import re

from xmlgenerator.randomization import Randomizer

__all__ = ['Substitutor']

_pattern = re.compile(
    r'\{\{\s*(?:(?P<function>\S*?)(?:\(\s*(?P<argument>[^)]*)\s*\))?\s*(?:\|\s*(?P<modifier>.*?))?)?\s*}}')

logger = logging.getLogger(__name__)


class Substitutor:
    def __init__(self, randomizer: Randomizer):
        self.randomizer = randomizer
        self._local_context = {}
        self._global_context = {}
        self.providers_dict = {
            # local scope functions
            'source_filename': lambda args: self._local_context["source_filename"],
            'source_extracted': lambda args: self._local_context["source_extracted"],
            'output_filename': lambda args: self.get_output_filename(),

            'any': lambda args: self._any(args),
            'regex': lambda args: self._regex(args),
            'uuid': lambda args: self.randomizer.uuid(),
            'number': lambda args: self._number(args),
            'date': lambda args: self._date_formatted(args),

            'last_name': lambda args: self.randomizer.last_name(),
            'first_name': lambda args: self.randomizer.first_name(),
            'middle_name': lambda args: self.randomizer.middle_name(),
            'address_text': lambda args: self.randomizer.address_text(),
            'administrative_unit': lambda args: self.randomizer.administrative_unit(),
            'house_number': lambda args: self.randomizer.house_number(),
            'city_name': lambda args: self.randomizer.city_name(),
            'country': lambda args: self.randomizer.country(),
            'postcode': lambda args: self.randomizer.postcode(),
            'company_name': lambda args: self.randomizer.company_name(),
            'bank_name': lambda args: self.randomizer.bank_name(),
            'phone_number': lambda args: self.randomizer.phone_number(),
            'inn_fl': lambda args: self.randomizer.inn_fl(),
            'inn_ul': lambda args: self.randomizer.inn_ul(),
            'ogrn_ip': lambda args: self.randomizer.ogrn_ip(),
            'ogrn_fl': lambda args: self.randomizer.ogrn_fl(),
            'kpp': lambda args: self.randomizer.kpp(),
            'snils_formatted': lambda args: self.randomizer.snils_formatted(),
            'email': lambda args: self.randomizer.email(),
        }

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

        logger.debug('reset local context...')
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

            provider_func = lambda: func_lambda(func_args)

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

    def _any(self, args):
        separated_args = str(args).split(sep=",")
        options = [i.strip(' ').strip("'").strip('"') for i in separated_args]
        return self.randomizer.any(options)

    def _regex(self, args):
        pattern = args.strip("'").strip('"')
        return self.randomizer.regex(pattern)

    def _number(self, args):
        left_bound, right_bound = (int(i) for i in str(args).split(sep=","))
        return str(self.randomizer.integer(left_bound, right_bound))

    def _date_formatted(self, args):
        date_from, date_until = (i.strip(' ').strip("'").strip('"') for i in str(args).split(sep=","))
        random_date = self.randomizer.random_datetime(date_from, date_until)
        return random_date.strftime("%Y%m%d")
