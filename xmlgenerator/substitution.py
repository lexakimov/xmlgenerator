import logging
import re
from typing import NamedTuple, Optional

from xmlgenerator.configuration import VariablesConfig
from xmlgenerator.randomization import Randomizer

__all__ = ['Substitutor', 'ExpressionSyntaxError']

logger = logging.getLogger(__name__)


class Substitutor:
    def __init__(self, randomizer: Randomizer, variables_config: VariablesConfig):
        self._randomizer = randomizer
        self._variables_config = variables_config
        self._local_context = {}
        self._global_context = {}
        self._providers_dict = {
            # scope access functions
            'global': lambda args: self._get_variable_from_scope(args, self._global_context, 'global'),
            'local': lambda args: self._get_variable_from_scope(args, self._local_context, 'local'),

            # local scope functions
            'root_element': lambda args: self._local_context["root_element"],
            'source_filename': lambda args: self._local_context["source_filename"],
            'source_extracted': lambda args: self._local_context["source_extracted"],
            'output_filename': lambda args: self.get_output_filename(),

            'any': lambda args: self._any(args),
            'any_from': lambda args: self._any_from(args),
            'regex': lambda args: self._regex(args),
            'uuid': lambda args: self._randomizer.uuid(),
            'number': lambda args: self._number(args),
            'date': lambda args: self._date_formatted(args),

            'first_name': lambda args: self._randomizer.first_name(args),
            'last_name': lambda args: self._randomizer.last_name(args),
            'middle_name': lambda args: self._randomizer.middle_name(args),
            'phone_number': lambda args: self._randomizer.phone_number(args),
            'email': lambda args: self._randomizer.email(args),

            'country': lambda args: self._randomizer.country(args),
            'city': lambda args: self._randomizer.city(args),
            'street': lambda args: self._randomizer.street(args),
            'house_number': lambda args: self._randomizer.house_number(args),
            'postcode': lambda args: self._randomizer.postcode(args),
            'administrative_unit': lambda args: self._randomizer.administrative_unit(args),

            'company_name': lambda args: self._randomizer.company_name(args),
            'bank_name': lambda args: self._randomizer.bank_name(args),

            # ru_RU only
            'inn_fl': lambda args: self._randomizer.inn_fl(),
            'inn_ul': lambda args: self._randomizer.inn_ul(),
            'ogrn_ip': lambda args: self._randomizer.ogrn_ip(),
            'ogrn_fl': lambda args: self._randomizer.ogrn_fl(),
            'kpp': lambda args: self._randomizer.kpp(),
            'snils_formatted': lambda args: self._randomizer.snils_formatted(),
        }

    def reset_context(self, xsd_filename, root_element_name, config_local):
        self._local_context.clear()
        self._local_context["source_filename"] = xsd_filename
        self._local_context["root_element"] = root_element_name

        source_filename = config_local.source_filename
        matches = re.search(source_filename, xsd_filename).groupdict()
        source_extracted = matches['extracted']
        self._local_context["source_extracted"] = source_extracted

        output_filename = config_local.output_filename
        resolved_value = self._process_expression(output_filename)
        self._local_context['output_filename'] = resolved_value

        logger.debug('reset local context...')
        logger.debug('local_context["root_element"]     = %s', root_element_name)
        logger.debug('local_context["source_filename"]  = %s', xsd_filename)
        logger.debug('local_context["source_extracted"] = %s (extracted with regexp %s)', source_extracted, source_filename)
        logger.debug('local_context["output_filename"]  = %s', resolved_value)

    def _get_variable_from_scope(self, args: Optional[str], context: dict, scope_name: str):
        variable_name = args.strip(' ').strip("'").strip('"') if args is not None else None
        if not variable_name:
            raise RuntimeError(f"{scope_name.capitalize()} variable name is not specified")

        logger.debug('get variable "%s" from %s context...', variable_name, scope_name)
        value = context.get(variable_name)
        if value is None:
            logger.debug('variable "%s" not found in %s context', variable_name, scope_name)
            config_field = scope_name if scope_name != 'global' else 'global_'
            definitions = getattr(self._variables_config, config_field, None)

            expression = definitions.get(variable_name)
            if expression is None:
                raise RuntimeError(f"{scope_name.capitalize()} variable '{variable_name}' is not defined")

            value = self._process_expression(expression)
            logger.debug('variable "%s" added to %s context. value: %s', variable_name, scope_name, value)
            context[variable_name] = value
        else:
            logger.debug('variable "%s" is found in %s context. value: %s', variable_name, scope_name, value)

        return value

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
        result_value: str = expression
        resolved_substitutions = []
        subexpressions = _parse_subexpressions(expression)
        for se in subexpressions:
            func_name = se.function
            func_args = se.argument
            func_lambda = self._providers_dict.get(func_name)
            if func_lambda is None:
                raise RuntimeError(f"Unknown function {func_name}")

            resolved_value = func_lambda(func_args)
            resolved_substitutions.append((se.start, se.end, str(resolved_value)))

        for start, end, replacement in reversed(resolved_substitutions):
            result_value = result_value[:start] + replacement + result_value[end:]

        logger.debug('expression resolved to value: %s', result_value)
        return result_value

    def _any(self, args):
        separated_args = str(args).split(sep=",")
        options = [i.strip(' ').strip("'").strip('"') for i in separated_args]
        return self._randomizer.any(options)

    def _any_from(self, args):
        file_path = args.strip(' ').strip("'").strip('"')
        return self._randomizer.any_from(file_path)

    def _regex(self, args):
        pattern = args.strip("'").strip('"')
        return self._randomizer.regex(pattern)

    def _number(self, args):
        left_bound, right_bound = (int(i) for i in str(args).split(sep=","))
        return str(self._randomizer.integer(left_bound, right_bound))

    def _date_formatted(self, args):
        date_from, date_until = (i.strip(' ').strip("'").strip('"') for i in str(args).split(sep=","))
        random_date = self._randomizer.random_datetime(date_from, date_until)
        return random_date.strftime("%Y%m%d")


class _ParsedExpression(NamedTuple):
    start: int
    end: int
    function: str
    argument: Optional[str]


class ExpressionSyntaxError(ValueError):
    def __init__(self, expression: Optional[str], position: int, description: str):
        super().__init__(f'Failed to parse expression: {expression}: {description} at position {position}')
        self.expression = expression
        # Clamp position to the expression boundaries to avoid IndexError when formatting
        self.position = self._clamp_position(position, expression)
        self.description = description

    @staticmethod
    def _clamp_position(position: int, expression: Optional[str]) -> int:
        if expression is None:
            return position
        return max(0, min(len(expression), position))

    def attach_expression(self, expression: str) -> None:
        self.expression = expression
        self.position = self._clamp_position(self.position, expression)


def _parse_subexpressions(expression: str) -> list[_ParsedExpression]:
    subexpressions: list[_ParsedExpression] = []
    cursor = 0
    while True:
        start = expression.find('{{', cursor)
        if start == -1:
            break
        end = expression.find('}}', start + 2)
        if end == -1:
            raise ExpressionSyntaxError(expression, len(expression), "missing closing '}}'")
        inner = expression[start + 2:end]
        try:
            function, argument = _parse_placeholder_inner(start, inner)
        except ExpressionSyntaxError as exc:
            exc.attach_expression(expression)
            raise
        subexpressions.append(_ParsedExpression(start, end + 2, function, argument))
        cursor = end + 2
    return subexpressions


def _parse_placeholder_inner(start: int, inner: str) -> tuple[str, Optional[str]]:
    inner_start = start + 2
    stripped_inner = inner.strip()
    if not stripped_inner:
        raise ExpressionSyntaxError(None, inner_start, "placeholder is empty")

    leading_ws = len(inner) - len(inner.lstrip())
    text_offset = inner_start + leading_ws
    function, argument = _parse_function_call(start, stripped_inner, text_offset)

    return function, argument


def _parse_function_call(start: int, text: str, absolute_offset: int) -> tuple[str, Optional[str]]:
    stripped = text.strip()
    leading_ws = len(text) - len(text.lstrip())
    content_offset = absolute_offset + leading_ws
    if not stripped:
        raise ExpressionSyntaxError(None, content_offset, "function name is missing")

    idx = 0
    while idx < len(stripped) and not stripped[idx].isspace() and stripped[idx] != '(':
        idx += 1

    function = stripped[:idx]

    remainder = stripped[idx:]
    if remainder:
        remainder_lstrip = remainder.lstrip()
        remainder_offset = content_offset + idx + (len(remainder) - len(remainder_lstrip))
        if not remainder_lstrip.startswith('('):
            raise ExpressionSyntaxError(None, remainder_offset, f"unexpected text after function name '{function}'")
        argument, rest, rest_offset = _extract_arguments(start, remainder_lstrip, remainder_offset)
        if rest.strip():
            rest_lstrip = rest.lstrip()
            leftover_offset = rest_offset + (len(rest) - len(rest_lstrip))
            if rest_lstrip.startswith(')'):
                raise ExpressionSyntaxError(None, leftover_offset, "unexpected ')'")
            raise ExpressionSyntaxError(None, leftover_offset, "unexpected text after arguments")
    else:
        argument = None

    return function, argument


def _extract_arguments(start: int, text: str, absolute_offset: int) -> tuple[Optional[str], str, int]:
    depth = 0
    quote: Optional[str] = None
    i = 0
    while i < len(text):
        ch = text[i]
        if i == 0:
            if ch != '(':
                raise ExpressionSyntaxError(None, absolute_offset, "arguments must start with '('")
            depth = 1
            i += 1
            continue
        if quote:
            if ch == quote:
                quote = None
        else:
            if ch in ('"', "'"):
                quote = ch
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    argument = text[1:i]
                    argument = argument.strip() if argument else None
                    rest = text[i + 1:]
                    rest_offset = absolute_offset + i + 1
                    return argument, rest, rest_offset
        i += 1

    raise ExpressionSyntaxError(None, start, "missing closing ')' for placeholder")
