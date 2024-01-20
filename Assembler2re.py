import json
from time import perf_counter
import sys
import os
import Preprocessor


class Assembler:
    def __init__(self, path, dest):
        self.path = path
        self.dest = dest
        self.file = None
        self.include = []
        self.machine_file = []
        self.flags = {'z':1,'nz':2,'c':4,'nc':8,'neg':16,'pos':32}
        # zero, not zero, carry, no carry, negative, positive
        self.regs = {'r0','r1','r2','r3','r4','r5','r6','r7','r8','r9','r10','r11','r12','r13','r14','r15','r16','r17','r18','r19','r20','r21','r22','r23','r24','r25','r26','r27','r28','r29','r30','r31','p0','p1','p2','p3'}

    def lex(self, path):
        tokens = Preprocessor.tokenise(path)
        code, defines, labels = Preprocessor.create_contex_tables(tokens)
        self.file = File(code, defines, labels)

    @staticmethod
    def file_path(file_name):
        directory = os.getcwd()
        path = os.path.join(directory , file_name)
        return path

    def combine_files(self):
        with open("Joined.txt", "a") as target:
            for file in self.include:
                path = self.file_path(file)
                with open(path, "r") as source:
                    target.write(source.read() + "\n")

    @staticmethod
    def opcode_num(opcode):
        opcodes = {'orr':0,'and':3,'xor':6,'nor':9,'nand':12,'add':15,'cad':19,'adc':22,'sub': 23,'bsb':27,'sbb': 28,'sar':29,'sal':34,'ror':39,'rol':40,'rcr':41,'rcl':42,'ldi':43,'jmp':44,'jif':45,'pst':46,'pld':47,'lod':48,'lfp':49,'str':50,'sfp':51,'pop':52,'psh':53,'cwd':54,'imul':55,'cmb':56,'movsx':57,'call':58,'ret':59,'hlt':63}
        return opcodes.get(opcode)

    @staticmethod
    def expected_op_number(opcode):
        expected_ops = {'mov':2,'orr':3,'and':3,'xor':3,'nor':3,'nand':3,'add':3,'cad':3,'adc':3,'sub': 3,'bsb':3,'sbb': 3,'sar':3,'sal':3,'ror':2,'rol':2,'rcr':2,'rcl':2,'jmp':1,'jif':2,'pst':2,'pld':2,'lod':2,'lfp':2,'str':2,'sfp':2,'pop':1,'psh':1,'cwd':2,'imul':2,'cmb':3,'movsx':2,'call':1,'ret':0,'hlt':0}
        return expected_ops.get(opcode)

    @staticmethod
    def valid_op_maps(opcode):
        op_maps = {
            'orr': {'rrr','rri','rrm','rmr'},
            'and': {'rrr','rri','rrm','rmr'},
            'xor': {'rrr','rri','rrm','rmr'},
            'nor': {'rrr','rri','rrm','rmr'},
            'nand': {'rrr','rri','rrm','rmr'},
            'add': {'rrr','rri','rir','rmr','rrm','mrr'},
            'cad': {'rrr','rmr','rrm','mrr'},
            'adc': {'rrr'},
            'sub': {'rrr','rri','rrm','mrr'},
            'bsb': {'rrr'},
            'sbb': {'rrr'},
            'sar': {'irr'},
            'sal': {'irr'},
            'ror': {'rr'},
            'rol': {'rr'},
            'rcr': {'rr'},
            'rcl': {'rr'},
            'jmp': {'i'},
            'jif': {'ii'},
            'pst': {'rr'},
            'pld': {'rr'},
            'lpf': {'rr'},
            'mov': {'rr','ri','mr','rm'},
            'str': {'mr'},
            'sfp': {'rr'},
            'pop': {'r'},
            'psh': {'r'},
            'cwd': {'rr'},
            'imul': {'rr'},
            'cmb': {'rrr'},
            'mosx': {'rr'},
            'call': {'i'},
            'ret': {''},
            'hlt': {''}
        }
        return op_maps.get(opcode)

    @staticmethod
    def to_int(number: str) -> int:
        num_type = number[:2]
        if num_type == "0b":
            return(int(number, base = 2))
        elif num_type == "0x":
            return(int(number, base = 16))
        elif num_type == "0o":
            return(int(number, base = 8))
        else: 
            return(int(number))

    def print_binery_output(self):
        for i in range(0, len(self.machine_file) - 1, 2):
            low16 = bin(self.machine_file[i][1])[2:]
            prettylow16 = (16 - len(low16))*'0' + low16
            high16 = bin(self.machine_file[i+1][1])[2:]
            prettyhigh16 = (16 - len(high16))*'0' + high16
            print(f'{i >> 1}: {prettylow16} : {self.machine_file[i][1]}, {prettyhigh16}: {self.machine_file[i+1][1]}')

    @staticmethod
    def Error1(line_num, strline, error):
        sys.exit(f"{'-'*50}\nAssembly failed in Line {line_num}:\n\n    {strline}\n\n{error}\n{'-'*50}")

    @staticmethod
    def Error2(line_num, strline, newstrline, error):
        sys.exit(f"{'-'*50}\nAssembly failed in Line {line_num}:\n\n    {strline}\n -> {newstrline}\n\n{error}\n{'-'*50}")

    def translate_to_machine_code(self):
        for line_num, line in enumerate(self.file.code):
            machine_word_1 = 0
            machine_word_2 = 0
            opcode = line[0].lower()
            strline = opcode + " " + ", ".join(line[1:])
            expected = self.expected_op_number(opcode)
            op_number = len(line) - 1

            if expected == None:
                self.Error1(line_num, strline, f"Error: Opcode \'{opcode}\' could not be resolved.")
            elif expected != op_number:
                if expected > op_number:
                    self.Error1(line_num, strline, f"Error: Missing arguments. \'{opcode}\' expected {expected}, got {op_number}.")
                else:
                    self.Error1(line_num, strline, f"Error: Too many arguments. \'{opcode}\' expected {expected}, got {op_number}.")
            
            interpreted = []
            op_map = ''
            new = []
            bswp = False

            for k, operand in enumerate(line[1:]):
                definition = self.file.all.get(operand)
                new_operand = ''
                if definition == None:
                    new_operand = operand
                else:
                    new_operand = definition

                new.append(str(new_operand))

                if new_operand in self.regs:
                    interpreted.append(int(new_operand[1:]))
                    op_map += 'r'
                    continue
                elif type(new_operand) == int:
                    interpreted.append(new_operand)
                    op_map += 'i'
                    continue
                elif new_operand[0] in {'0','1','2','3','4','5','6','7','8','9'}:
                    interpreted.append(self.to_int(new_operand))
                    op_map += 'i'
                    continue
                elif new_operand[0] == '[' and new_operand[-1] == ']':
                    if k == 0:
                        bswp = True
                    try:
                        interpreted.append(self.to_int(new_operand[1:-1]))
                        op_map += 'm'
                        continue
                    except:
                        self.Error1(line_num, strline, f"Error: Operand \'{operand}\' could not be resolved.")
                else:
                    resolution = self.flags.get(new_operand)
                    if resolution:
                        interpreted.append(resolution)
                        op_map += 'i'
                        continue
                    self.Error1(line_num, strline, f"Error: Operand \'{operand}\' could not be resolved.")

            newstrline = opcode + ' ' + ', '.join(new)
            # checck operands given are legal

            valid_maps = self.valid_op_maps(opcode)
            if op_map not in valid_maps:
                self.Error2(line_num, strline, newstrline, f"Error: operands given are not valid.")

            # calculate opcode based on the operand map
            start = 0

            if opcode in {'orr', 'and', 'xor', 'nor', 'nand', 'add', 'cad', 'sub', 'bsb'}:
                if op_map[0] == 'm':
                    if opcode == 'cad':
                        machine_word_1 += (self.opcode_num(opcode) + 2) << 10
                    else:
                        machine_word_1 += (self.opcode_num(opcode) + 3) << 10
                elif op_map[1] == 'i' or op_map[2] == 'i':
                    machine_word_1 += (self.opcode_num(opcode) + 1) << 10
                elif op_map[1] == 'm' or op_map[2] == 'm':
                    machine_word_1 += (self.opcode_num(opcode) + 2) << 10
                else:
                    machine_word_1 += self.opcode_num(opcode) << 10
            elif opcode in {'sar', 'sal'}:
                if interpreted[0] not in {1,2,3,4,8}: self.Error2(line_num, strline, newstrline, f"Error: shifting by: \'{interpreted[0]}\' bits is not supported.\nYou may only shift by: 1,2,3,4 or 8 bits at a time.")
                if interpreted[0] == 8:
                    machine_word_1 += (self.opcode_num(opcode) + 4) << 10
                else:
                    machine_word_1 += (self.opcode_num(opcode) + interpreted[0] - 1) << 10
                interpreted.pop(0)
                op_map = 'rr'
            elif opcode == 'mov':
                if op_map == 'rr':
                    pass
                elif op_map == 'ri':
                    machine_word_1 += 1024  # ori
                elif op_map == 'mr':
                    machine_word_1 += self.opcode_num('str') << 10
                    start = 1
                elif op_map == 'rm':
                    machine_word_1 += self.opcode_num('lod') << 10
            elif opcode == 'jif':
                machine_word_1 += self.opcode_num('jif') << 10
                machine_word_1 += interpreted[0] << 4
                interpreted.pop(0)
                op_map = 'i'
                pass
            else:   
                machine_word_1 += self.opcode_num(opcode) << 10

            for indx, char in enumerate(op_map):
                if char == 'i' or char == 'm':
                    machine_word_2 = interpreted[indx]
                    op_map = op_map.replace(char, '')
                    interpreted.pop(indx)
                    break

            if bswp:
                temp = interpreted[1]
                interpreted[1] = interpreted[0]
                interpreted[0] = temp

            if opcode in {'str','sfp','psh','imul'}:
                start = 1

            for indx, op in enumerate(interpreted):
                if start + indx >= 2:
                    machine_word_2 += op << 11
                else:
                    if (indx + start) == 0:
                        machine_word_1 += op << 5
                    else:
                        machine_word_1 += op            

            self.machine_file.append([line_num*2, machine_word_1])
            self.machine_file.append([(line_num*2) + 1, machine_word_2])

    def Assemble(self):
        tokens = Preprocessor.tokenise(self.path)
        self.include = Preprocessor.search_includes(tokens)
        with open("Joined.txt", "w") as target:
            with open(self.path, "r") as main:
                target.write(main.read() + "\n\n")
        # merge included files into one files for assembly
        if self.include != []:
            self.combine_files()
        #preprocess main file
        self.lex(self.file_path("Joined.txt"))
        # convert to machhine code
        self.translate_to_machine_code()
        with open (self.dest, 'w') as f:
            json.dump(self.machine_file, f)
        # write binery to file to check if correct
        # tempororay
        with open ("bin.txt", 'w') as f:
            for i in range(0, len(self.machine_file) - 1, 2):
                low16 = bin(self.machine_file[i][1])[2:]
                prettylow16 = ((16 - len(low16))*'0' + low16)
                high16 = bin(self.machine_file[i+1][1])[2:]
                prettyhigh16 = (16 - len(high16))*'0' + high16
                f.write(f'{prettylow16} : {self.machine_file[i][1]}, {prettyhigh16}: {self.machine_file[i+1][1]}\n')
        
        #self.print_binery_output()
        print(f"Assembly finished with no errors.")    
        print(f"Size = {len(self.machine_file) * 2} bytes, {len(self.machine_file)} words, {len(self.machine_file) >> 1} instructions")


class File:
    def __init__(self, code = [], defines = {}, labels = {}) -> None:
        self.code = code
        self.defines = defines
        self.labels = labels
        self.all = defines | labels
    def search_defines(self, word: str) -> str:
        return self.defines.get(word)
    def search_labels(self, label: str) -> int:
        return self.labels.get(label)


def Timer(func) -> None:
    def wrapper(*args, **kwargs):
        start = perf_counter()
        func(*args, **kwargs)
        diff = perf_counter() - start
        print(f'Function {func.__name__} took {diff*1000:.4f}ms')
    return(wrapper)

@Timer
def main():
    A = Assembler(path = "C:\\Users\\squas\\VS\SM CPU\\Assmebler_programs\Test.txt", dest = "C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\387990\\2817316401\\data.json")
    A.Assemble()

main()
