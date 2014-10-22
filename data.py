import random

def withify_gen(noun):
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

def correct_nouns(source_file, dest_file):
	with open(source_file) as sf, open(dest_file, 'w') as df:
		for line in sf:
			noun = line.strip()
			print(noun, withify_gen(noun), file=df, sep=',')

def load_nouns(source_file):
	result = {}
	with open(source_file) as f:
		for line in f:
			elements = line.strip().split(',')
			result[elements[0]] = tuple(elements[1:])
	return result


nouns = {}
noun_forms = {}

def register_nouns(category, source_file):
	result = load_nouns(source_file)
	nouns[category] = list(result.keys())
	noun_forms.update(result)

def withify(noun):
	return noun_forms[noun][0]

def random_noun(category):
	return random.choice(nouns[category])

register_nouns("names", "names_hu.txt")
