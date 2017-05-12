import re

pp=0
code = []
symbols = {}
symbols1={}
loopend = []
startif = []
opcodes = {}
symbol_table={}
pass2 = []
pass1=[]
if_ = 0
loop_ = 0
var_ = 0
label=''

def replace(pass_instr):
	pass1=[]
	for line in pass_instr:
		if line[13]=='J':
			instr=line.split()[-1]
			pos=line.find(instr)
			instr=line[:pos]+' '+symbol_table[int(instr)]+'\n'
			pass1.append(instr)
		else:
			pass1.append(line)
	return pass1
			
def label_check(label):
	if label:
		label=''
	return label

def generate(string,pp,label):
	instr='#'+(str(pp)).ljust(4,' ')
	if label:
		instr+=' '+label+' '
		symbol_table[pp]=label
	instr=instr.ljust(12,' ')
	instr+=' '+string
	return instr

def assemble(files):
	if_ = 0
	loop_ = 0
	var_ = 0
	pp=0
	label=''
	
	f=open('opcode_len.txt','r')
	data=f.read()
	f.close()
	lines=data.splitlines()
	for line in lines:
		line=line.split(' ')
		opcodes[line[0]]=int(line[1])
		
	assign=re.compile('var(.*?)=(.*)')
	macro=re.compile('@(.*?)(.*)')
	ext=re.compile('extern (.*)')
	arith=re.compile('(.*?)=(.*?)[\+\-\&\|](.*?)')
	arith_add=re.compile('(.*?)=(.*?)\+(.*)')
	arith_sub=re.compile('(.*?)=(.*?)\-(.*)')
	arith_or=re.compile('(.*?)=(.*?)\|(.*)')
	arith_and=re.compile('(.*?)=(.*?)\&(.*)')

	for filen in files:
		filename=filen.split('.')[0]
		symbols[filename]= {}
		symbols1[filename]= {}
		f=open("Input/"+filen,'r')
		data=f.read()
		f.close()
		lines=data.splitlines()
		for line in lines:
			line=line.strip()
			if assign.match(line):
				asign=line[3:]
				a=re.search(r'(.*?)=(.*)',asign)
				vari = a.group(1).strip()
				val = a.group(2).strip()

				code.append('JMP '+str(pp+opcodes['JMP']+opcodes['DC'])+'\n')
				instr=generate(code[-1],pp,label)
				label=label_check(label)

				pass2.append(instr)
				pp += opcodes['JMP']

				code.append('DC '+val+'\n')
				symbols[filename][vari] = str(pp)		
				symbols1[filename][vari] = val		
				var_+=1
				instr=generate(code[-1],pp,vari)
				label=label_check(label)
				pass2.append(instr)
				pp += opcodes['DC']
				label='var'+str(var_)

			elif macro.match(line):
				asign=line[1:]
				a=re.search(r'(.*?)\s(.*)',asign)
				vari = a.group(1).strip()
				val = a.group(2).strip()

				code.append('JMP '+str(pp+opcodes['JMP']+opcodes['DM'])+'\n')
				instr=generate(code[-1],pp,label)
				label=label_check(label)

				pass2.append(instr)
				pp += opcodes['JMP']

				code.append('DM '+val+'\n')
				symbols[filename][vari] = str(pp)		
				symbols1[filename][vari] = val		
				var_+=1
				instr=generate(code[-1],pp,vari0)
				label=label_check(label)
				pass2.append(instr)
				pp += opcodes['DM']
				label='var'+str(var_)
			elif ext.match(line):
				var=line[6:].strip()
				symbols[filename][var]='extern'+var
				symbols1[filename][var]='extern'+var

			elif arith.match(line):
				a=re.search(r'(.*?)=(.*?)[\+\-\&\|](.*)',line)
				if arith_add.match(line):
					op='ADD '
					opi='ADI '
				elif arith_sub.match(line):
					op='SUB '
					opi='SUI '
				elif arith_and.match(line):
					op='ANA '
					opi='ANI '
				elif arith_or.match(line):
					op='ORA '
					opi='ORI '
				vari = a.group(1).strip()
				var1 = a.group(2).strip()
				var2 = a.group(3).strip()
				if var1.isdigit() and var2.isdigit():
					code.append('MVI A, '+var1+'\n')

					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['MVI']

					code.append(opi+var2+'\n')

					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)

					pp += opcodes['ADI']

					code.append('STA '+symbols[filename][vari]+'\n')

					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['STA']										

				elif var1.isdigit():
					code.append('LDA '+symbols[filename][var2]+'\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['LDA']

					code.append('MOV B, A\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['MOV']

					code.append('MVI A, '+var1+'\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['MVI']

					code.append(op+'B\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['ADD']

					code.append('STA '+symbols[filename][vari]+'\n')				
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['STA']

				elif var2.isdigit():
					code.append('LDA '+symbols[filename][var1]+'\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['LDA']
					
					code.append(opi+var2+'\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['ADI']
					
					code.append('STA '+symbols[filename][vari]+'\n')										
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['STA']					
				else:
					code.append('LDA '+symbols[filename][var2]+'\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['MVI']

					code.append('MOV B, A\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['MOV']

					code.append('LDA '+symbols[filename][var1]+'\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['LDA']

					code.append(op+'B\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['ADD']

					code.append('STA '+symbols[filename][vari]+'\n')					
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['STA']

			elif line.startswith('loop'):
				a=re.search(r'loop(.*)',line)
				count=a.group(1).strip()
				code.append('PUSH D\n')
				instr=generate(code[-1],pp,label)
				label=label_check(label)
				pass2.append(instr)
				pp += opcodes['PUSH']		
				loop_ += 1
				code.append('MVI E, '+count+'\n')
				instr=generate(code[-1],pp,label)
				label=label_check(label)
				pass2.append(instr)
				pp += opcodes['MVI']						
				loopend.append(str(pp))
				label='loop'+str(loop_)

			elif line.startswith('endloop'):
				code.append('MOV A, E\n')
				instr=generate(code[-1],pp,label)
				label=label_check(label)
				pass2.append(instr)
				pp += opcodes['MOV']
				
				code.append('SUI 1\n')
				instr=generate(code[-1],pp,label)
				label=label_check(label)
				pass2.append(instr)
				pp += opcodes['SUI']
				
				code.append('MOV E, A\n')
				instr=generate(code[-1],pp,label)
				label=label_check(label)
				pass2.append(instr)
				pp += opcodes['MOV']
				
				code.append('JNZ '+loopend.pop()+'\n')
				instr=generate(code[-1],pp,label)
				label=label_check(label)
				pass2.append(instr)
				pp += opcodes['JNZ']				
				
				code.append('POP D'+'\n')											
				instr=generate(code[-1],pp,label)
				label=label_check(label)
				pass2.append(instr)
				pp += opcodes['POP']				

			elif line.startswith('if'):
				a=re.search(r'if(.*?)\((.*?)\)',line)
				cond = a.group(2)
				if '>' in cond:
					a=re.search(r'(.*?)>(.*)',cond)
					var1 = a.group(1).strip()
					var2 = a.group(2).strip()
					code.append('LDA '+symbols[filename][var1]+'\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['LDA']

					code.append('MOV B, A\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['MOV']

					code.append('LDA '+symbols[filename][var2]+'\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['LDA']

					code.append('SUB B\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					startif.append(len(code))
					pp += opcodes['SUB']
					
					code.append('JP\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)

					pp += opcodes['JP']
					
					code.append('JZ\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['JZ']
				elif '=' in cond:
					a=re.search(r'(.*?)=(.*)',cond)
					var1 = a.group(1).strip()
					var2 = a.group(2).strip()
					code.append('LDA '+symbols[filename][var1]+'\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['LDA']
					code.append('MOV B, A\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['MOV']
					code.append('LDA '+symbols[filename][var2]+'\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['LDA']
					code.append('SUB B\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					startif.append(len(code))
					pp += opcodes['SUB']
					code.append('JNZ\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp +=opcodes['JNZ']
				
			elif line.startswith('endif'):
				lineno=startif.pop()
				if code[lineno] is 'JNZ\n':
					code[lineno] = 'JNZ '+str(pp)+'\n'
					pass2[lineno]=pass2[lineno][:-1]+' '+str(pp)+'\n'
				elif code[lineno] is 'JP\n':
					code[lineno] = 'JP '+str(pp)+'\n'
					pass2[lineno]=pass2[lineno][:-1]+' '+str(pp)+'\n'
					code[lineno+1] = 'JZ '+str(pp)+'\n'
					pass2[lineno+1]=pass2[lineno+1][:-1]+' '+str(pp)+'\n'
				if_+=1
				label='if'+str(if_)
			else:
				a=re.search(r'(.*?)=(.*)',line)
				var=a.group(1).strip()
				val=a.group(2).strip()
				if val.isdigit():
					code.append('MVI A, '+val+'\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['MVI']
					code.append('STA '+symbols[filename][var]+'\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp+=opcodes['STA']
				else:
					code.append('LDA '+symbols[filename][val]+'\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp += opcodes['LDA']
					code.append('STA '+symbols[filename][var]+'\n')
					instr=generate(code[-1],pp,label)
					label=label_check(label)
					pass2.append(instr)
					pp +=opcodes['STA']

		# code.append('HLT\n')
		# pp += 1
	code.append('HLT\n')
	instr=generate(code[-1],pp,label)
	label=label_check(label)
	pass2.append(instr)
	filename=files[-1].split('.')[0]
	pass1=replace(pass2)
	

	tcode=''.join(code)
	ttcode=tcode.splitlines()
	tpass2=''.join(pass2)
	ttpass2=tpass2.splitlines()
	tpass1=''.join(pass1)
	ttpass1=tpass1.splitlines()
	store=[]

	for i in ttpass1:
		if i[13:16]=='HLT':
			value=int(i[1:4])

	# countLC=1
	# for filen in files:
	# 	filename=filen.split('.')[0]
	# 	symbols[filename]= {}
	# 	f=open("Input/"+filen,'r')
	# 	data=f.read()
	# 	f.close()
	# 	lines=data.splitlines()
	# 	for line in lines:
	# 		line=line.strip()
	# 		if assign.match(line):
	# 			asign=line[3:]
	# 			a=re.search(r'(.*?)=(.*)',asign)
	# 			vari = a.group(1).strip()
	# 			val = a.group(2).strip()
	# 			symbols[filename][vari] = str(value+countLC)
	# 			countLC+=1				
	# 		elif macro.match(line):
	# 			asign=line[1:]
	# 			a=re.search(r'(.*?)\s(.*)',asign)
	# 			vari = a.group(1).strip()
	# 			val = a.group(2).strip()
	# 			symbols[filename][vari] = str(value+countLC)
	# 			countLC+=1

	mark=0
	tstring=""
	for i in ttpass1:
		print i
		if i[13:14]!='D':
			tstring+=i+"\n"
		else:
			store.append(i)
		if i[13:16]=='HLT':
			mark=1
	mark2=0
	countLC=1
	for i in store:
		k=""
		count=0

		if mark==1:
			for j in i:
				if j=='#':
					mark2=1
					k+=j
					continue
				if mark2==1:
					k+=str(value+countLC)
					countLC+=1
					mark2=0
					continue
				if mark2==0:
					if value >= 100 and count==0:
						count=-1
						continue
					if count==-1:
						count=1
						continue
					if count==0:
						count+=1
						continue
					k+=j
					continue
		tstring+=k+"\n"
	store=[]	

	f=open("Output/"+filename+"1"+'.pass1','w')
	f.write(tstring)
	f.close()
	
	mark=0
	tstring=""
	for i in ttcode:
		if i[0:1]!='D':
			tstring+=i+"\n"
		else:
			store.append(i)
		if i[0:3]=='HLT':
			mark=1
	for i in store:
		tstring+=i+"\n"
	store=[]
	f=open("Output/"+filename+"1"+'.asm','w')
	f.write(tstring)
	f.close()

	mark=0
	tstring=""	
	for i in ttpass2:
		if i[13:14]!='D':
			tstring+=i+"\n"
		else:
			store.append(i)
		if i[13:16]=='HLT':
			mark=1
	mark2=0
	countLC=1
	for i in store:
		k=""
		count=0
		if mark==1:
			for j in i:
				if j=='#':
					mark2=1
					k+=j
					continue
				if mark2==1:
					k+=str(value+countLC)
					countLC+=1
					mark2=0
					continue
				if mark2==0:
					if value >= 100 and count==0:
						count=-1
						continue
					if count==-1:
						count=1
						continue
					if count==0:
						count+=1
						continue
					k+=j
		tstring+=k+"\n"
	store=[]
	f=open("Output/"+filename+"1"+'.pass2','w')
	f.write(tstring)
	f.close()

	f=open("Output/"+filename+'.asm','w')
	f.write(''.join(code))
	f.close()

	f=open("Output/"+filename+'.pass1','w')
	f.write(''.join(pass1))
	f.close()	
	print filename+'.pass1 file generated.'
	
	f=open("Output/"+filename+'.pass2','w')
	f.write(''.join(code))
	f.close()	
	print filename+'.pass2 file generated.'

	# print symbol_table	
	
	return (symbols1,symbols,symbol_table)