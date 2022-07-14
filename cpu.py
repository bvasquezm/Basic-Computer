import csv
import threading

# ----------
# README: 
# La carpeta con los archivos .csv (/tests) debe estar en el mismo directorio que el script.
# los archivos .csv deben tener el siguiente formato:
#   - input: se debe ingresar solo el nombre del archivo sin extensión, no maneja excepciones
# 	- primera linea: nombre de las columnas
# 	- resto de lineas: datos de las filas
#   - lineas 2 y 3: contienen los valores iniciales y finales de las direcciones (al igual que los ejemplos
#   - opcode: separado un espacio de los operandos " "
#   - NO deben haber espacios aparte del señalado en el punto anterior
#   - instrucciones separadas por ";", operandos separados por ","
# ----------

class Run(threading.Thread):
	def __init__(self, P):
		super().__init__()
		self.processors = P
		self.instructions = [] # lista de instrucciones
	
	def run(self):
		self.divide_instructions()
		for j in range(len(self.instructions[0])):
			for i in range(len(self.processors)):
				self.processors[i].run(self.instructions[i][j])

	# divide instructions by processor
	def divide_instructions(self):
		div_instructions = [[] for i in range(len(self.instructions[0]))]
		for i in range(len(self.instructions)):
			for j in range(len(self.instructions[0])):
				cmd = self.decode_instruction(self.instructions[i][j])
				div_instructions[j].append(cmd)
		self.instructions = div_instructions

	def decode_instruction(self, instruction):
		instruction = instruction.split(" ")
		opcode = instruction[0]
		if opcode != 'NOP':
			operands = instruction[1].split(",")
			return (opcode, operands)
		return (opcode)

	def display_values(self, DIRS_FINAL):
		print("=== INPUT FINAL VALUES ===")
		print(DIRS_FINAL)
		print("=== RUNNING VALUES ===")
		print(self.processors[0].DIRS)

class Processor(threading.Thread):
	DIRS = dict()
	global_dir = dict()

	def __init__(self, name):
		super().__init__(name=name)
		self.A = 0
		self.B = 0
		self.last_dir = None

	def run(self, instruction):
		self.execute(*instruction)

	def execute(self, cmd, *args):
		if cmd == 'MOV':
			self.mov(cmd, *args[0])
		elif cmd == 'ADD':
			self.add(*args[0])
		elif cmd == 'SUB':
			self.sub(*args[0])
		elif cmd == 'NOP':
			self.nop()
		
	def mov(self, cmd, reg, op):
		if op[0] == '(':
			self.assign_reg_value(reg, self.fetch_dir_value(op[1:-1]))
			self.write_dir_value(op[1:-1], self.fetch_reg_value(reg))
			self.set_dirs(op[1:-1], cmd, reg, op)
		elif reg[0] == '(':
			self.write_dir_value(reg[1:-1], self.fetch_reg_value(op))
		else:
			self.assign_reg_value(reg, int(op))

	def add(self, reg1, reg2):
		self.assign_reg_value(reg1, self.A + self.B)
		if self.last_dir != None:
			self.write_dir_value(self.last_dir, self.fetch_reg_value(reg1))

	def sub(self, reg1, reg2):
		if reg1 == 'A':
			self.assign_reg_value(reg1, self.A - self.B)
		elif reg1 == 'B':
			self.assign_reg_value(reg1, self.B - self.A)
		if self.last_dir != None:
			self.write_dir_value(self.last_dir, self.fetch_reg_value(reg1))

	def nop(self):
		return

	def assign_reg_value(self, reg, value):
		if reg == 'A':
			self.A = value
		elif reg == 'B':
			self.B = value

	def fetch_reg_value(self, reg):
		if reg == 'A':
			return self.A
		elif reg == 'B':
			return self.B

	def fetch_dir_value(self, direction):
		return int(self.DIRS[direction])

	def write_dir_value(self, direction, value):
		self.DIRS[direction] = value

	def set_dirs(self, direction, cmd, *args):
		self.last_dir = direction
		self.check_error(cmd, *args)
		self.global_dir[direction] = self.name

	def check_error(self, cmd, *args):
		if self.global_dir[self.last_dir] != self.name and self.global_dir[self.last_dir] != '':
			print(f'INCONSISTENCY FOUND in {self.name}: {cmd} {args}')

# Fetch initial data from csv file
def fetch_init_data(csvfile, DIRS_INIT, DIRS_FINAL):
	file = csv.reader(csvfile, delimiter=';')
	header = next(file)
	header_list = ' '.join(header).split(' ')
	file_list = list(file)
	instructions = list()

	# Fetch directions data from csv file
	for i in range(len(file_list)):
		instructions.append(file_list[i])
		for j in range(len(file_list[0])):
			if(i == 0 and j > 3):
				DIRS_INIT[header_list[j]] = file_list[i][j]
			elif(i == 1 and j > 3):
				DIRS_FINAL[header_list[j]] = file_list[i][j]
			if (j == len(file_list[0]) - 1):
				instructions[i] = instructions[i][:4] # removes direction data
	
	return instructions

def generate_global_dirs(DIRS_INIT):
	global_dir = DIRS_INIT.copy()
	for key in DIRS_INIT.keys():
		global_dir[key] = ''
	return global_dir

def run_program(file_name, R):
	DIRS_INIT = dict() # Inital direction dictionary
	DIRS_FINAL = dict() # Final direction dictionary

	csvfile = open(file_name, 'r')
	instructions = fetch_init_data(csvfile, DIRS_INIT, DIRS_FINAL)
	R.instructions = instructions
	Processor.DIRS = DIRS_INIT # Set directions to processors as class atribute
	Processor.global_dir = generate_global_dirs(DIRS_INIT)
	R.start()
	R.join()
	R.display_values(DIRS_FINAL)

	csvfile.close()

if __name__ == "__main__":
	# Example: t1, t2, t3 are valid inputs	
	input_file = input("Enter input file name (t{i} format): ")
	P = list() # Processors list
	for i in range(4):
		P.append(Processor('P' + str(i)))
	R = Run(P)
	# Must have tests dir in same directory as this file
	run_program(f"tests2/{input_file}.csv", R) 
	
    



