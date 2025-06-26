# Config Parse

## class Config(text_config)

        :param config: text based config
        :return: None

        Parses a text based config into self.lines

        lines structure is a dictionary in the form
        {line_number: {'command': str, 'indent': str, 'parent': int, 'children': [int, int, ...]}, ...}


### search_lines(list_of_regex_strings)

        Does an iterative search through all sections specified in the search_command_list and
        returns a list of all lines matching the final expression in the list.

        If source_lines is unspecified, the search will be done on the full config.

          search_lines(['^sdwan$', '^interface', '^tunnel-interface'])
          Returns all instances of ^tunnel-interface in the ^interface section(s) of the ^sdwan$ sections
          You can find the interfaces by using find_parent on the items in the list

          search_lines(['^interface'])
          Returns all interface commands in the base config

### print_section(line_number)

    
        Prints the section in standard indent format starting with line number section_line.
        Default is the full config.
        
### print_regex_section(regex_string)

        Prints all sections that contain the line_regex. Only searches the direct children of the source lines.

          print_regex_section('^interface') will print the config of all interfaces
    
### find_parents(line_number)
    
        Returns all parents, grandparents, etc. of a given line.

### list_of_lines(dict_format_config)

        Converts lines from a dictionary to a list.
        Each list item is a dictionary that includes the line number.

# py_bandwidth

Returns a csv file of all upstream and downstream bandwidth values on tunnel interfaces for all edges in a vManage.

Edit vManage info in py_bandwidth.py and run:

> python py_bandwidth.py

# py_ints

Returns a csv file of all ints in a switch.  Run against a text config:

> python py_ints config.txt
