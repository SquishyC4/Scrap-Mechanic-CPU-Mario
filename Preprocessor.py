from Assembler import Timer

def tokenise(path) -> list:
    with open(path, 'r') as f:
        Tokenised = []
        temp = ''
        for line in f:
            tokens = []
            for char in line:
                if char == ';': break
                elif char not in {' ', ',','\n'}: temp += char
                elif temp: 
                    tokens.append(temp)
                    temp = ''
            if temp: tokens.append(temp)
            if tokens: Tokenised.append(tokens)
    return(Tokenised)

def search_includes(tokens):
    includes = []
    i = 0
    while tokens[i][0] == "#include":
        includes.append(tokens[i][1])
        i += 1
    return includes

def create_contex_tables(tokens) -> (list, dict, dict):
    code = []
    defines = {}
    labels = {}
    line_count = 0
    i = 0
    while i < len(tokens):
        line = tokens[i]
        element = line[0]
        if element[0] != '#' and element[0] != '.' and element[-1] != ':':
            code.append(line)
            line_count += 1
        elif element[0] == '#':
            if element[1] == 'd':     #define
                i += 1
                while i < len(tokens) and tokens[i][0][-1] != ':':
                    defines.update({tokens[i][0]:tokens[i][1]})
                    i += 1
                continue
        elif element[0] == '.':
            labels.update({element[0:]:line_count})
        elif element[-1] == ':':
            labels.update({element[:-1]:line_count})
        i += 1
    return code, defines, labels