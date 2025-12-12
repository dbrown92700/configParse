import re


class Config:

    def __init__(self, config: str):

        """
        :param config: text based config
        :return: None

        Parses a text based config into self.lines

        lines structure is a dictionary in the form
        {line_number: {'command': str, 'indent': str, 'parent': int, 'children': [int, int, ...]}, ...}
        """

        self.lines = {0: {'command': '', 'indent': -1, 'parent': None, 'children': []}}

        def iterate_config(remaining_config: list, indent: int, parent=0):
            # Recursive function to read all lines in the config
            lines = {}
            this_line = parent
            while remaining_config:
                line = remaining_config[0]
                text = line.lstrip()
                line_indent = len(line) - len(text)
                if (not text) or (text[0] == '!'):
                    remaining_config.pop(0)
                    continue
                if line_indent == indent:
                    this_line += 1
                    lines[this_line] = {'command': text, 'indent': indent, 'parent': parent, 'children': []}
                    remaining_config.pop(0)
                if line_indent < indent:
                    return lines, this_line
                if line_indent > indent:
                    sub_lines, next_line = iterate_config(remaining_config, line_indent, parent=this_line)
                    for sub_line in sub_lines:
                        if sub_lines[sub_line]['indent'] == line_indent:
                            lines[this_line]['children'].append(sub_line)
                        lines[sub_line] = sub_lines[sub_line]
                    this_line = next_line
            return lines, this_line

        base_lines, config_length = iterate_config(config.lstrip().splitlines(), indent=0)
        for base_line in base_lines:
            self.lines[base_line] = base_lines[base_line]
            if base_lines[base_line]['indent'] == 0:
                self.lines[0]['children'].append(base_line)

    def search_lines(self, search_command_list: list, source_lines=[], recursive=False, include_parents=False) -> dict:

        """
        Does an iterative search through all sections specified in the search_command_list and
        returns a list of all lines matching the final expression in the list.

        If source_lines is unspecified, the search will be done on the full config.

          search_lines(['^sdwan$', '^interface', '^tunnel-interface'])
          Returns all instances of ^tunnel-interface in the ^interface section(s) of the ^sdwan$ sections
          You can find the interfaces by using find_parent on the items in the list

          search_lines(['^interface'])
          Returns all interface commands in the base config

        """

        if type(search_command_list) is str:
            search_command_list = [search_command_list]
        if len(search_command_list) > 1:
            recursive = False
        if not source_lines:
            search_lines = self.lines[0]['children']
        else:
            search_lines = source_lines.copy()
        next_lines = []
        found_lines = {}
        for num, command in enumerate(search_command_list):
            for line in search_lines:
                if re.search(command, self.lines[line]['command']):
                    if num+1 < len(search_command_list):
                        next_lines = next_lines + self.lines[line]['children']
                    else:
                        if include_parents:
                            parents = self.find_parents(line)
                            for parent in parents:
                                if parent not in found_lines:
                                    found_lines[parent] = self.lines[parent]
                        found_lines[line] = self.lines[line]
                if recursive and self.lines[line]['children']:
                    recursive_lines = self.search_lines(search_command_list,
                                                        source_lines=self.lines[line]['children'],
                                                        recursive=True, include_parents=include_parents)
                    found_lines = found_lines | recursive_lines


            search_lines = next_lines.copy()
            next_lines = []

        return found_lines

    def print_section(self, section_line=0, recursive=True):
    
        """
        Prints the section in standard indent format starting with line number section_line.
        Input can be an int for a single section, list for multiple sections, or dict of lines.
        Default is the full config.

        If recursive is False, only prints the lines without children.
        """
        if isinstance(section_line, int):
                section_line = [section_line]
        if isinstance(section_line, dict):
                section_line = list(section_line.keys())
        def recursive_print(lines: list):
            for line in lines:
                print(f'{int(line):04}: {self.lines[line]["indent"] * " "}{self.lines[line]["command"]}')
                if recursive:
                    recursive_print(self.lines[line]['children'])
        recursive_print(section_line)

    def print_regex_section(self, line_regex: list, source_lines=[]):
    
        """
        Prints all sections that contain the line_regex. Only searches the direct children of the source lines.

          print_regex_section('^interface') will print the config of all interfaces
        """

        if isinstance(line_regex, str):
            line_regex = [line_regex]
        sections = self.search_lines(line_regex, source_lines)
        for section in sections:
            self.print_section(section)

    def find_parents(self, line):
    
        """
        Returns all parents, grandparents, etc. of a given line.
        """

        parents = []
        while self.lines[line]['parent']:
            line = self.lines[line]['parent']
            parents.append(line)
        parents.reverse()
        return parents

    @staticmethod
    def list_of_lines(lines: dict):

        """
        Converts lines from a dictionary to a list.
        Each list item is a dictionary that includes the line number.
        """

        return_lines = []
        for line in lines:
            return_line = lines[line]
            return_line['number'] = line
            return_lines.append(return_line)
        return return_lines
        