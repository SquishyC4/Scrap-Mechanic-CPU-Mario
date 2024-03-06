# for the old cpu (neobium) only

import json
from time import perf_counter
import sys

def Timer(func) -> None:
    def wrapper(*args, **kwargs):
        start = perf_counter()
        func(*args, **kwargs)
        diff = perf_counter() - start
        print(f'{func.__name__} took {diff*1000:.5f}ms')
    return(wrapper)

def tokenise(path) -> list:
    with open(path, 'r') as f:
        Tokenised = []
        for line in f:
            tokens = []
            temp = ''
            for char in line:
                if char == '#' or char == ';': break
                if char not in {' ', ',','\n'}:
                    temp += char
                else:
                    if temp:
                        tokens.append(temp)
                        temp = ''
            if temp: tokens.append(temp)
            if tokens: Tokenised.append(tokens)
    #print(Tokenised)
    return(Tokenised)

def log_labels(Code) -> tuple[dict, list]:
    # takes the tokenised form
    labels = {}
    for index, line in enumerate(Code):
        if line[0][0] == '.':
            labels.update({line[0]: index})
            Code[index].remove(line[0])
    #print(labels)
    return(labels, Code)

def to_int(number: str) -> int:
    num_type = number[:2]
    if num_type == "0b":
        return(int(number, base = 2))
    elif num_type == "0x":
        return(int(number, base = 16))
    elif num_type == "0o":
        return(int(number, base = 8))
    elif type(number) == float:
        raise TypeError
    else:
        return(int(number))

def get_opcode(op) -> int:
    opcodes = {'ORR':0,'MOV':0,'AND':1,'XOR':2,'NAND':3,'NOR':4,'ADD':5,'ADC':6,'FAD':7,'SUB':8,'SBC':9,'FSB':10,'LSH':11,'RSH':12,'ROL':13,'ROR':14,'RCL':15,'RCR':16,'CMP':17,'LPC':18,'LDI':19,'JMP':20,'JTP':21,'JIF':22,'PST':23,'PLD':24,'LOD':25,'LFP':26,'STR':27,'SFP':28,'PSH':29,'POP':30,'HLT':31}
    return(opcodes.get(op) << 19)

@Timer
def Assemble(asm_path: str = "", dest: str = '') -> None:
    tokens = tokenise(asm_path)
    labels, Code = log_labels(tokens)

    data = [] # 2d array of [address, data] pairs
    location = 0 # address
    for line_num, line in enumerate(Code):
        #print(line)
        Machine_Code = 0
        opcode = line[0].upper()
        Machine_Code += get_opcode(opcode)
        # Destination in first arg
        if opcode in {'ORR','AND','XOR','NAND','NOR','MOV','ADD','ADC','FAD','SUB','SBC','FSB','LSH','RSH','ROL','ROR','RCL','RCR','LPC','LDI','PST','PLD','LOD','LFP','POP'}:
            Machine_Code += int(line[1][-1]) << 16
        # regA in second
        if opcode in {'ORR','AND','XOR','NAND','NOR','MOV','ADD','ADC','FAD','SUB','SBC','FSB','LSH','RSH','ROL','ROR','RCL','RCR','PST','PLD','LFP'}:
            Machine_Code += int(line[2][-1]) << 13
        # regB in third
        if opcode in {'ORR','AND','XOR','NAND','NOR','ADD','ADC','FAD','SUB','SBC','FSB'}:
            Machine_Code += int(line[3][-1]) << 10
        # regA first
        if opcode in {'CMP','JTP','SFP'}:
            Machine_Code += int(line[1][-1]) << 13
        # regB second
        if opcode in {'CMP','SFP'}:
            Machine_Code += int(line[2][-1]) << 10
        # PSH requires data in b reg
        if opcode == "PSH":
            Machine_Code += int(line[-1][-1]) << 10
        # Store using special immediate
        if opcode == 'STR':
            Machine_Code += int(line[1][-1]) << 10
            s_imm = list(bin(to_int(line[2])))
            s_imm = s_imm[2:]
            if len(s_imm) < 16:
                s_imm = ['0' for i in range(16 - len(s_imm))] + s_imm
            imm = ['0', 'b'] + s_imm[:6] + ['0', '0', '0'] + s_imm[6:]
            str_si = ''
            for i in imm: str_si += i
            int_si = int(str_si, base = 0)
            Machine_Code += int_si
        # Jump type with immeditate
        if opcode in {'JMP','JIF'}:
            if line[-1][0] == '.':
                Machine_Code += labels.get(line[-1])
            elif line[-1][0] in {'+', '-'}:
                Machine_Code += line_num + int(line[-1])
            else:
                Machine_Code += to_int(line[1])
        #other immeditates
        if opcode in {'LDI','LOD'}:
            Machine_Code += to_int(line[-1])
        # JIF deal
        if opcode == 'JIF':
            Flags = ['z','n','c','gr','le','neq']
            if line[1].lower() in Flags:
                Machine_Code += (Flags.index(line[1].lower()) + 1) << 16
            else:
                print("Assembly failed")
                print('-'*50+'\n'+'\''+line[1]+'\'','isnt recognised as a flag\ntry a flag out of:',Flags,'\n','-'*50)
                sys.exit(1)

        data.append([location, Machine_Code])
        location += 1

    print(f'\ncode is {len(tokens)} lines long\n')

    with open(dest, 'w') as f:
        json.dump(data, f) # write to the json file

if __name__ == "__main__":
    assembly_code_path = "C:\\Users\\squas\\VS\\SM CPU\\Tic Tac Toe.txt"
    destination_file = "C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\387990\\2817316401\\data.json"
    Assemble(asm_path = assembly_code_path, dest = destination_file)
