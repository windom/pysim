
with open("names_hu.txt") as f:
	names = [line.strip() for line in f]

def withify(noun):
	if noun[-1] in 'aou':
		return noun + "val"
	elif noun[-1] in 'ei':
		return noun + "vel"
	elif noun[-1] == 'y':
		idx = -3
		while not noun[idx] in 'aouei':
			idx -= 1		
		if noun[idx] in 'aou':
			suf = 'al'
		else:
			suf = 'el'
		return noun[:-2] + noun[-2]*2 + noun[-1] + suf
	else:
		if noun[-2] == noun[-1]:
			idx = -3
			suf = ""
		else:
			idx = -2
			if noun[-1] != 'x':
				suf = noun[-1]
			else:
				suf = "-"
		while not noun[idx] in 'aouei':
			idx -= 1
		if noun[idx] in 'aoui':
			suf += 'al'
		else:
			suf += 'el'		
		return noun + suf

