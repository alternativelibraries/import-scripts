# Import the lxml module for xml support
from lxml import etree
import codecs

# Document element
unimarc = etree.Element("unimarc")

# Load all of the table files, exported into xml from mysql
bookcallno = etree.parse("bookcallno.xml")
bookdetails = etree.parse("bookdetails.xml")
booksubjects = etree.parse("booksubjects.xml")
booksubjects_fr = etree.parse("booksubjects_fr.xml")

# Add a new column to each table, containing contiguous count values for iteration indices
bookcallno = etree.parse("bookcallno.xml")
context = etree.iterwalk(bookcallno, events=('start',), tag="table")
c = 0
for start, book in context:
	counter = etree.SubElement(book, "column", name="count")
	cstr = str(c)
	counter.text = cstr
	c += 1

# Iterate through all record IDs, all subsequent steps be done once for each record (but iteration in skipped if location doesn't match)
#for count in xrange(0, 3227):
for count in range(0, 3227):

#for count,ID in enumerate(xrange(1, 3440)):
#count = 0
#ID = "0"
#while ID != "3440":
	#count += 1
	#ID = str(count)
	#IDs could include a location code?
	#ID = count
	#ID = str(ID)

#for idx,item in enumerate(list):

#fulltitle = ''.join(bookd[0].xpath("./column[@name='title']/text()"))

	# bookc contains an element with the callno row for this record
	bookc = bookcallno.xpath("//column[@name='count' and text()='%s']/ancestor::table" % count)
	ID = ''.join(bookc[0].xpath("./column[@name='id']/text()"))
	#if ID == ("283" or "1086"):
	#	continue
	#print(ID + " - " + str(len(bookc)))
	#print(etree.tostring(bookc[0], pretty_print=True))

	# Skip iteration if number# doesn't match (CHANGE FOR LOCATION)
	# QPIRG-C is number2, QPIRG-M is number3.
	if bookc[0].xpath("./column[@name='number2']/text()") == ['NULL']:
		continue

	# Record element
	notice = etree.SubElement(unimarc, "notice")

	# Mystery elements, required by PMB for each record
	rs = etree.SubElement(notice, "rs")
	rs.text = "n"
	dt = etree.SubElement(notice, "dt")
	dt.text = "a"
	bl = etree.SubElement(notice, "bl")
	bl.text = "m"
	hl = etree.SubElement(notice, "hl")
	hl.text = "0"
	el = etree.SubElement(notice, "el")
	el.text = "1"
	ru = etree.SubElement(notice, "ru")
	ru.text = "i"

	# ID field, unique for each record
	fID = etree.SubElement(notice, "f", c="001")
	fID.text = ID

	# Meta data field, the same for each record except for creation date
	fmeta = etree.SubElement(notice, "f", c="100", ind="  ")
	smeta = etree.SubElement(fmeta, "s", c="a")
	smeta.text = "20140916u        u  u0frey0103    ba"

	# bookd contains an element with the "bookdetails" row for this record
	bookd = bookdetails.xpath("//column[@name='id' and text()='%s']/ancestor::table" % ID)

	# Title field 
	ftitle = etree.SubElement(notice, "f", c="200", ind="1 ")
	stitle1 = etree.SubElement(ftitle, "s", c="a")
	# Get title field from old database
	fulltitle = ''.join(bookd[0].xpath("./column[@name='title']/text()"))
	#print(fulltitle)
	# If title has a ':', split it into Title and Subtitle fields
	twotitles = fulltitle.split(":", 1)
	if len(twotitles) == 1:
		stitle1.text = fulltitle
	else:
		stitle1.text = twotitles[0]
		stitle2 = etree.SubElement(ftitle, "s", c="e")
		stitle2.text = twotitles[1]

	# ISBN may need to be reformatted? Test the old version.
	fisbn = etree.SubElement(notice, "f", c="010", ind="  ")
	sisbn = etree.SubElement(fisbn, "s", c="a")
	isbn = ''.join(bookd[0].xpath("./column[@name='isbn']/text()"))
	sisbn.text = isbn.replace("-", "")
	
	# Language field
	flang = etree.SubElement(notice, "f", c="101", ind="0 ")
	slang1 = etree.SubElement(flang, "s", c="a")
	# Convert old database language labels into PMB codes
	language = ''.join(bookd[0].xpath("./column[@name='lang']/text()"))
	#print(language)
	
	# ' or "fran?ais" ' could be used in python3?
	if ("English" or "english") in language:
		slang1.text = "eng"
	#	print("Recorded as eng")
	elif ("Fre" or "fre" or "fran" or "Fran") in language:
		slang1.text = "fre"
		#print("Recorded as fre")
		#print("   ")
	else:
		slang2 = etree.SubElement(flang, "s", c="a")
		slang1.text = "eng"
	#	print("Recorded as both")
	#print (' ') 

# multilingual? How to sort on PMB to find the ones that have two languages. Possibly with SQL sorting queries. 

	# Description field (usually blank)
	fdesc = etree.SubElement(notice, "f", c="330", ind="  ")
	sdesc = etree.SubElement(fdesc, "s", c="a")
	sdesc.text = ''.join(bookd[0].xpath("./column[@name='descr']/text()"))

	# Author (or editor) field
	fauth = etree.SubElement(notice, "f", c="700", ind=" 1")
	slast = etree.SubElement(fauth, "s", c="a")
	sfirst = etree.SubElement(fauth, "s", c="b")
	stype = etree.SubElement(fauth, "s", c="4")
	# Get author field from old database 
	fullname = ''.join(bookd[0].xpath("./column[@name='author']/text()"))
	# Split single string "lastname, firstname" into two different strings (twonames[0] for lastname, and twonames[1] for firstname)
	twonames = fullname.split(",", 1)
	# If name contains "ed.", change the PMB author type to editor
	if "ed." in fullname:
		stype.text = "340"
	else:
		stype.text = "070"

	# Remove "ed." from names, and copy names to their respective fields
	if len(twonames) == 2:
		slast.text = twonames[0].replace("ed.", "")
		sfirst.text = twonames[1].replace("(ed.)", "")
	elif len(twonames) == 1:
		slast.text = twonames[0].replace("ed.", "")
		sfirst.text = ""

# more often multiple authors in the coauthor field

	# Joint author (or editor) field 
	fjauth = etree.SubElement(notice, "f", c="701", ind=" 1")
	sjlast = etree.SubElement(fjauth, "s", c="a")
	sjfirst = etree.SubElement(fjauth, "s", c="b")
	sjtype = etree.SubElement(fjauth, "s", c="4")
	# Get coauthor field from old database
	fullname = ''.join(bookd[0].xpath("./column[@name='coauthor']/text()"))
	# Split single field "lastname, firstname" into two different fields
	twonames = fullname.split(",", 1)
	# If name contains "ed.", change the PMB author type to editor
	if "ed." in fullname:
		sjtype.text = "340"
	else:
		sjtype.text = "070"

	# Remove "ed." from names, and copy names to their respective fields
	if len(twonames) == 2:
		sjlast.text = twonames[0].replace("ed.", "")
		sjfirst.text = twonames[1].replace("(ed.)", "")
	elif len(twonames) == 1:
		sjlast.text = twonames[0].replace("ed.", "")
		sjfirst.text = ""
	
	# Publisher field, including year
	fpub = etree.SubElement(notice, "f", c="210", ind="  ")
	spub = etree.SubElement(fpub, "s", c="c")
	syear = etree.SubElement(fpub, "s", c="d")
	spub.text = ''.join(bookd[0].xpath("./column[@name='publisher']/text()"))
	syear.text = ''.join(bookd[0].xpath("./column[@name='year']/text()"))
	 
	# pmb opac url containing isbn (without any dashes)
	furl = etree.SubElement(notice, "f", c="896", ind="  ")
	surl = etree.SubElement(furl, "s", c="a")
	ISBNdashes = ''.join(bookd[0].xpath("./column[@name='isbn']/text()"))
	ISBN = ISBNdashes.replace("-", "")
	surl.text = './opac_css/getimage.php?url_image=&amp;noticecode=' + ISBN + '&amp;vigurl='

	# 995 copy field
	f995 = etree.SubElement(notice, "f", c="995", ind="  ")
	s995a = etree.SubElement(f995, "s", c="a")
	s995c = etree.SubElement(f995, "s", c="c")
	s995f = etree.SubElement(f995, "s", c="f")
	s995k = etree.SubElement(f995, "s", c="k")
	s995o = etree.SubElement(f995, "s", c="o")
	s995r = etree.SubElement(f995, "s", c="r")
	s995u = etree.SubElement(f995, "s", c="u")
	s995a.text = "AlternativeLibraries"
	s995c.text = "AlternativeLibraries"
	# CHANGE callno# BASED ON LOCATION
	# QPIRG-C is number2, QPIRG-M is number3.
	callno = ''.join(bookc[0].xpath("./column[@name='callno2']/text()"))
	s995f.text = callno
	s995k.text = callno
	s995o.text = "av"
	
	# Get the material type from the old database, and convert it into the equivalent type for PMB
	material1 = ''.join(bookd[0].xpath("./column[@name='material']/text()"))
	
	if material1 == "book":
		material2 = "Livre/Book"
		mediacode = "bb"
	elif material1 == "zine":
		material2 = "Zine"
		mediacode = "zi"
	elif material1 == "periodical/magazine":
		material2 = "Magazine/Journal"
		mediacode = "mj"
	elif material1 == "vhs video":
		material2 = "Cassette vid"
		mediacode = "cv"
	elif material1 == "dvd video":
		material2 = "DVD video"
		mediacode = "dv"
	elif material1 == "cd-audio":
		material2 = "CD audio"
		mediacode = "cd"
	elif material1 == "graphic work" or "posters":
		material2 = "Art"
		mediacode = "ar"
	elif material1 == "NULL" or "":
		material2 = "Null"
		mediacode = "na"
	else:
		material2 = "Autre / Other" #ADD THIS TO THE PMB ITEM MATERIAL TYPE LIST
		mediacode = "au"
	
	s995r.text = mediacode
	
	callnoarray = callno.split(" ", 1)
	scode = callnoarray[0]
	#print(scode)
	#print( )
	
	", "
	
	#Conversion of call number codes into ids for corresponding sections on PMB
	#This section needs to change completely for a difference location

	if "ACT" == scode:
		s995u.text = "108"
	elif "ANA" == scode:
		s995u.text = "109"
	elif "BIC" == scode:
		s995u.text = "110"
	elif "PER" == scode:
		s995u.text = "111"
	elif "BOD" == scode:
		s995u.text = "112"
	elif "CHI" == scode:
		s995u.text = "113"
	elif scode in {"POL", "COL"}:
		s995u.text = "114"
	elif "CON" == scode:
		s995u.text = "115"
	elif "REF" == scode:
		s995u.text = "116"
	elif "DIS" == scode:
		s995u.text = "117"
	elif "DRU" == scode:
		s995u.text = "118"
	elif "ECO" == scode:
		s995u.text = "119"
	elif scode in {"EDU", "STU"}:
		s995u.text = "120"
	elif "ENV" == scode:
		s995u.text = "121"
	elif "FEM" == scode:
		s995u.text = "122"
	elif "FIC" == scode:
		s995u.text = "123"
	elif "FOO" == scode:
		s995u.text = "124"
	elif "GEN" == scode:
		s995u.text = "125"
	elif "HEA" == scode:
		s995u.text = "126"
	elif "DIY" == scode:
		s995u.text = "127"
	elif "HUM" == scode:
		s995u.text = "128"
	elif "IMM" == scode:
		s995u.text = "129"
	elif "IND" == scode:
		s995u.text = "130"
	elif "WOR" == scode:
		s995u.text = "131"
	elif "LEG" == scode:
		s995u.text = "132"
	elif "MED" == scode:
		s995u.text = "133"
	elif "MIS" == scode:
		s995u.text = "134"
	elif "PAR" == scode:
		s995u.text = "135"
	elif "BRU" == scode:
		s995u.text = "136"
	elif "ERO" == scode:
		s995u.text = "137"
	elif "PRI" == scode:
		s995u.text = "138"
	elif "QUE" == scode:
		s995u.text = "139"
	elif "RAC" == scode:
		s995u.text = "140"
	elif "PHI" == scode:
		s995u.text = "141"
	elif "SEL" == scode:
		s995u.text = "142"
	elif "VIO" == scode:
		s995u.text = "143"
	elif "UNP" == scode:
		s995u.text = "144"
	elif "WAR" == scode:
		s995u.text = "145"

	else:
		s995u.text = "146"
		print(fulltitle)
		print(scode)
		print(s995u.text)
		print(" ")
	
	# 996 copy field
	f996 = etree.SubElement(notice, "f", c="996", ind="  ")
	s996f = etree.SubElement(f996, "s", c="f")
	s996k = etree.SubElement(f996, "s", c="k")
	s996m = etree.SubElement(f996, "s", c="m")
	s996n = etree.SubElement(f996, "s", c="n")
	s996a = etree.SubElement(f996, "s", c="a")
	s996b = etree.SubElement(f996, "s", c="b")
	s996v = etree.SubElement(f996, "s", c="v")
	s996x = etree.SubElement(f996, "s", c="x")
	s996y = etree.SubElement(f996, "s", c="y")
	s996e = etree.SubElement(f996, "s", c="e")
	s996r = etree.SubElement(f996, "s", c="r")
	s9961 = etree.SubElement(f996, "s", c="1")
	s9962 = etree.SubElement(f996, "s", c="2")
	s9963 = etree.SubElement(f996, "s", c="3")

	# ID's could be distinguished by location, making conflicts less likely
	s996f.text = callno
	# CHANGE CALL NUMBER FOR LOCATION
	# callno = ''.join(bookc[0].xpath("./column[@name='callno3']/text()"))
	s996k.text = callno
	s996m.text = "00000000"
	s996n.text = "00000000"
	s996a.text = "AlternativeLibraries"
	s996b.text = "3"
	# CHANGE BASED ON LOCATION
	s996v.text = "QPIRG-Concordia"
	# SECTION NAME AND IMPORT CODE! 
	#if "1200 " in callno
	#	s996x.text = "Activism/Community Organizing"
	#	s996y.text = "1200"
	#elif "240 " in callno
	#	s996x.text = "Aging"
	#	s996y.text = "240"
	#else
	#	s996x.text = "testing"
	#	s996y.text = "TESTING"

	s996e.text = material2
	s996r.text = mediacode
	s9961.text = "Disponible / Available"
	s9962.text = "av"
	s9963.text = "1"

	# booksub contains an element with one of the "booksubject" rows for this record
	booksuben = booksubjects.xpath("//column[@name='id' and text()='%s']/ancestor::table" % ID)
	booksubfr = booksubjects_fr.xpath("//column[@name='id' and text()='%s']/ancestor::table" % ID)
	
	#606 subject headings
	f606en1 = etree.SubElement(notice, "f", c="606", ind="  ")
	s606en1 = etree.SubElement(f606en1, "s", c="a")
	s606en1.text = ''.join(booksuben[0].xpath("./column[@name='subject1']/text()"))
	
	f606en2 = etree.SubElement(notice, "f", c="606", ind="  ")
	s606en2 = etree.SubElement(f606en2, "s", c="a")
	s606en2.text = ''.join(booksuben[0].xpath("./column[@name='subject2']/text()"))
	
	f606en3 = etree.SubElement(notice, "f", c="606", ind="  ")
	s606en3 = etree.SubElement(f606en3, "s", c="a")
	s606en3.text = ''.join(booksuben[0].xpath("./column[@name='subject3']/text()"))

	
	if int(''.join(booksuben[0].xpath("./column[@name='id']/text()"))) <= 2831:
		f606fr1 = etree.SubElement(notice, "f", c="606", ind="  ")
		s606fr1 = etree.SubElement(f606fr1, "s", c="a")
		s606fr1.text = ''.join(booksubfr[0].xpath("./column[@name='subject1']/text()"))
	
		f606fr2 = etree.SubElement(notice, "f", c="606", ind="  ")
		s606fr2 = etree.SubElement(f606fr2, "s", c="a")
		s606fr2.text = ''.join(booksubfr[0].xpath("./column[@name='subject2']/text()"))
	
		f606fr3 = etree.SubElement(notice, "f", c="606", ind="  ")
		s606fr3 = etree.SubElement(f606fr3, "s", c="a")
		s606fr3.text = ''.join(booksubfr[0].xpath("./column[@name='subject3']/text()"))	
	

#For subject heading: authority number is mandatory.
#Get french and english subject headings from the old library

# create a file in python that is encoded with utf-8
f = codecs.open('QPIRGC-OUTPUT-full-final.xml', 'w',  "ISO-8859-1")
# convert the xml tree unimarc to a string encoded with utf-8, and then decode the utf-8. 
fw = etree.tostring(unimarc, pretty_print=True, encoding='ISO-8859-1').decode('ISO-8859-1')
# write the decoded xml string to the file
f.write(fw)
 
