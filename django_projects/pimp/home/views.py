# Create your views here.
from django.template import Context, loader
from django.shortcuts import render
from django.conf import settings
try:
	from django.utils import simplejson
except:
	import json as simplejson
from django.http import HttpResponse
from django.template import RequestContext
from fileupload.models import Sample

from rpy2.robjects.packages import importr
from rpy2 import robjects

# from django.templatetags.static import static
import json

def index(request):
	registration = settings.REGISTRATION_OPEN
	return render(request, 'index.html', {"home": True, 'registration': registration})

def about(request):
	return render(request, 'about.html', {"home": True})

def credits(request):
	return render(request, 'credits.html', {})

def chemical_library(request):
	return render(request, 'chemical_library.html', {"home": True})

def licence(request):
	return render(request, 'licence.html', {})
	
def polyomics_chemical_library(request):
	# url = static('metexplore_mapping.json')
	# url = "/opt/django/projects/django_projects/static/metexplore_mapping.json"
	# json_data = open(url)   
	# data1 = json.load(json_data)
	data1 = [{"idMysql":1766,"type":"biocyc","orgName":"Acinetobacter baumannii","strain":"SDF","nameBioSource":"AbSDF","source":"BioCyc","version":"18.0","TotalNumInchi":680,"MappedInchi":108,"MetexploreIdMapping":1709},{"idMysql":1770,"type":"biocyc","orgName":"Agrobacterium tumefaciens","strain":"C58","nameBioSource":"Atum","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":881,"MappedInchi":81,"MetexploreIdMapping":1710},{"idMysql":2026,"type":"biocyc","orgName":"Arabidopsis thaliana","strain":"col","nameBioSource":"ARA","source":"PlantCyc","version":"08-07-2014","TotalNumInchi":1547,"MappedInchi":101,"MetexploreIdMapping":1711},{"idMysql":809,"type":"import","orgName":"Arabidopsis thaliana","strain":"","nameBioSource":"AraGEM","source":"AraGEM","version":"NA","TotalNumInchi":1664,"MappedInchi":172,"MetexploreIdMapping":1712},{"idMysql":1771,"type":"biocyc","orgName":"Bacillus amyloliquefaciens","strain":"FZB42","nameBioSource":"Bamy","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":672,"MappedInchi":85,"MetexploreIdMapping":1713},{"idMysql":1772,"type":"biocyc","orgName":"Bacillus anthracis","strain":"Ames Ancestor","nameBioSource":"Bant","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":789,"MappedInchi":83,"MetexploreIdMapping":1714},{"idMysql":1773,"type":"biocyc","orgName":"Bacillus subtilis","strain":"168","nameBioSource":"Bsub","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":1143,"MappedInchi":145,"MetexploreIdMapping":1715},{"idMysql":1774,"type":"biocyc","orgName":"Bacillus thuringiensis","strain":"serovar konkukian str. 97-27","nameBioSource":"Bthu","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":766,"MappedInchi":82,"MetexploreIdMapping":1716},{"idMysql":1778,"type":"biocyc","orgName":"Bartonellatribocorum","strain":"CIP 105476","nameBioSource":"Btri","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":404,"MappedInchi":62,"MetexploreIdMapping":1717},{"idMysql":1767,"type":"biocyc","orgName":"Bos taurus","strain":"","nameBioSource":"BosT","source":"BioCyc","version":"18.0","TotalNumInchi":1271,"MappedInchi":147,"MetexploreIdMapping":1718},{"idMysql":1780,"type":"biocyc","orgName":"Bradyrhizobium japonicum","strain":"USDA 110","nameBioSource":"Bjap","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":1036,"MappedInchi":102,"MetexploreIdMapping":1719},{"idMysql":1976,"type":"biocyc","orgName":"Brassica rapa","strain":"","nameBioSource":"CHINESECABBAGE","source":"PlantCyc","version":"08-07-2014","TotalNumInchi":1569,"MappedInchi":94,"MetexploreIdMapping":1720},{"idMysql":1784,"type":"biocyc","orgName":"Buchnera aphidicola","strain":"Bp (Baizongia pistaciae)","nameBioSource":"BaphBP","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":243,"MappedInchi":53,"MetexploreIdMapping":1721},{"idMysql":1787,"type":"biocyc","orgName":"Burkholderia mallei","strain":"ATCC 23344","nameBioSource":"Bmal","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":915,"MappedInchi":95,"MetexploreIdMapping":1722},{"idMysql":1792,"type":"biocyc","orgName":"Candidatus Blochmannia pennsylvanicus","strain":"BPEN","nameBioSource":"Bpen","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":301,"MappedInchi":62,"MetexploreIdMapping":1723},{"idMysql":1981,"type":"biocyc","orgName":"Carica papaya","strain":"","nameBioSource":"PAPAYA","source":"PlantCyc","version":"08-07-2014","TotalNumInchi":1393,"MappedInchi":87,"MetexploreIdMapping":1724},{"idMysql":683,"type":"import","orgName":"Chlamydomonas reinhardtii","strain":"","nameBioSource":"iRC1080","source":"iRC1080","version":"NA","TotalNumInchi":1494,"MappedInchi":302,"MetexploreIdMapping":1725},{"idMysql":1800,"type":"biocyc","orgName":"Cupriavidus taiwanensis","strain":"LMG19424","nameBioSource":"Ctai","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":1760,"MappedInchi":159,"MetexploreIdMapping":1726},{"idMysql":1801,"type":"biocyc","orgName":"Desulfotalea psychrophila","strain":"Lsv54","nameBioSource":"Dpsy","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":654,"MappedInchi":73,"MetexploreIdMapping":1727},{"idMysql":1802,"type":"biocyc","orgName":"Erwinia carotovora","strain":"subsp. atroseptica SCRI1043","nameBioSource":"ERWCT87","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":849,"MappedInchi":90,"MetexploreIdMapping":1728},{"idMysql":681,"type":"import","orgName":"Escherichia coli","strain":"","nameBioSource":"iJO1366","source":"iJO1366","version":"NA","TotalNumInchi":1718,"MappedInchi":271,"MetexploreIdMapping":1729},{"idMysql":1812,"type":"biocyc","orgName":"Escherichia coli","strain":"B7A","nameBioSource":"ECOB7450","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":1012,"MappedInchi":156,"MetexploreIdMapping":1730},{"idMysql":677,"type":"import","orgName":"Escherichia coli","strain":"flux2","nameBioSource":"Ec_iAF1260","source":"Ec_iAF1260","version":"NA","TotalNumInchi":1407,"MappedInchi":622,"MetexploreIdMapping":1731},{"idMysql":1850,"type":"biocyc","orgName":"Helicobacter pylori","strain":"Shi470","nameBioSource":"HpylS","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":844,"MappedInchi":106,"MetexploreIdMapping":1732},{"idMysql":1747,"type":"biocyc","orgName":"Homo sapiens","strain":"","nameBioSource":"Hsap","source":"BioCyc","version":"18.0","TotalNumInchi":965,"MappedInchi":135,"MetexploreIdMapping":1733},{"idMysql":1379,"type":"Kegg","orgName":"Homo sapiens","strain":"","nameBioSource":"Homo sapiens (human) KEGG Genes Database","source":"Kegg","version":"","TotalNumInchi":1370,"MappedInchi":128,"MetexploreIdMapping":1734},{"idMysql":1363,"type":"SBML","orgName":"Homo sapiens","strain":"global network","nameBioSource":"Thiele2013 - Human metabolism global reconstruction (Recon 2) - model - version 2.02","source":"Recon2","version":"2.02","TotalNumInchi":2441,"MappedInchi":239,"MetexploreIdMapping":1735},{"idMysql":1852,"type":"biocyc","orgName":"Klebsiella pneumoniae","strain":"NTUH-K2044","nameBioSource":"KpneNTUH","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":949,"MappedInchi":86,"MetexploreIdMapping":1736},{"idMysql":1854,"type":"biocyc","orgName":"Lactobacillus casei","strain":"ATCC 334","nameBioSource":"Lcas","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":592,"MappedInchi":80,"MetexploreIdMapping":1737},{"idMysql":684,"type":"import","orgName":"Leishmania major","strain":"","nameBioSource":"iAC560","source":"iAC560","version":"NA","TotalNumInchi":774,"MappedInchi":191,"MetexploreIdMapping":1738},{"idMysql":1856,"type":"biocyc","orgName":"Listeria monocytogenes","strain":"EGD-e","nameBioSource":"Lmon","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":470,"MappedInchi":68,"MetexploreIdMapping":1739},{"idMysql":1974,"type":"biocyc","orgName":"Manihot esculenta","strain":"esculenta","nameBioSource":"CASSAVA","source":"PlantCyc","version":"08-07-2014","TotalNumInchi":1388,"MappedInchi":88,"MetexploreIdMapping":1740},{"idMysql":1746,"type":"biocyc","orgName":"MetaCyc","strain":"","nameBioSource":"Meta","source":"BioCyc","version":"18.0","TotalNumInchi":8736,"MappedInchi":471,"MetexploreIdMapping":1741},{"idMysql":1862,"type":"biocyc","orgName":"Methylobacterium sp. 4-46","strain":"","nameBioSource":"Msp4","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":912,"MappedInchi":101,"MetexploreIdMapping":1742},{"idMysql":2096,"type":"SBML","orgName":"Mus musculus","strain":"Global","nameBioSource":"Mus musculus GSM","source":"SBML","version":"mmu_May2008","TotalNumInchi":1957,"MappedInchi":224,"MetexploreIdMapping":1743},{"idMysql":1752,"type":"biocyc","orgName":"Mus musculus","strain":"","nameBioSource":"Mmus","source":"BioCyc","version":"18.0","TotalNumInchi":1538,"MappedInchi":186,"MetexploreIdMapping":1744},{"idMysql":2285,"type":"biocyc","orgName":"Musa acuminata","strain":"","nameBioSource":"MUSA","source":"Musacyc","version":"13-10-2014","TotalNumInchi":917,"MappedInchi":87,"MetexploreIdMapping":1745},{"idMysql":1864,"type":"biocyc","orgName":"Mycobacterium tuberculosis","strain":"H37Rv","nameBioSource":"Mtub","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":1307,"MappedInchi":127,"MetexploreIdMapping":1746},{"idMysql":1865,"type":"biocyc","orgName":"Mycoplasma genitalium","strain":"G37","nameBioSource":"Mgen","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":179,"MappedInchi":47,"MetexploreIdMapping":1747},{"idMysql":1869,"type":"biocyc","orgName":"Neisseria gonorrhoeae","strain":"NCCP11945","nameBioSource":"Ngon","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":460,"MappedInchi":69,"MetexploreIdMapping":1748},{"idMysql":1870,"type":"biocyc","orgName":"Orientia tsutsugamushi","strain":"Boryong","nameBioSource":"Otsu","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":216,"MappedInchi":50,"MetexploreIdMapping":1749},{"idMysql":2027,"type":"biocyc","orgName":"PlantCyc","strain":"","nameBioSource":"PLANT","source":"PlantCyc","version":"08-07-2014","TotalNumInchi":2434,"MappedInchi":113,"MetexploreIdMapping":1750},{"idMysql":1872,"type":"biocyc","orgName":"Pseudoalteromonas haloplanktis","strain":"TAC125","nameBioSource":"Phal","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":693,"MappedInchi":83,"MetexploreIdMapping":1751},{"idMysql":2670,"type":"SBML","orgName":"Rattus Norvegicus","strain":"","nameBioSource":"Whole Genome Metabolism - Rattus norvegicus","source":"BioModels","version":"Fev2015 (with URL)","TotalNumInchi":2191,"MappedInchi":130,"MetexploreIdMapping":1752},{"idMysql":1878,"type":"biocyc","orgName":"Rhizobium leguminosarum","strain":"bv. viciae 3841","nameBioSource":"Rleg","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":1107,"MappedInchi":102,"MetexploreIdMapping":1753},{"idMysql":1879,"type":"biocyc","orgName":"Rhodobacter sphaeroides","strain":"2.4.1","nameBioSource":"Rsph","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":873,"MappedInchi":93,"MetexploreIdMapping":1754},{"idMysql":1886,"type":"biocyc","orgName":"Rickettsia typhi","strain":"Wilmington","nameBioSource":"Rtyp","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":302,"MappedInchi":52,"MetexploreIdMapping":1755},{"idMysql":1753,"type":"biocyc","orgName":"Saccharomyces cerevisiae","strain":"S288C","nameBioSource":"Scer","source":"BioCyc","version":"18.0","TotalNumInchi":688,"MappedInchi":78,"MetexploreIdMapping":1756},{"idMysql":679,"type":"import","orgName":"Saccharomyces cerevisiae","strain":"","nameBioSource":"iMM904","source":"iMM904","version":"NA","TotalNumInchi":921,"MappedInchi":238,"MetexploreIdMapping":1757},{"idMysql":1985,"type":"biocyc","orgName":"Setaria italica","strain":"","nameBioSource":"SETARIA","source":"PlantCyc","version":"08-07-2014","TotalNumInchi":1504,"MappedInchi":97,"MetexploreIdMapping":1758},{"idMysql":1889,"type":"biocyc","orgName":"Shigella dysenteriae","strain":"Sd197","nameBioSource":"Sdys","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":905,"MappedInchi":144,"MetexploreIdMapping":1759},{"idMysql":2029,"type":"TrypanoCyc","orgName":"Trypanosoma brucei","strain":"","nameBioSource":"Tbru","source":"TrypanoCyc","version":"08-07-2014","TotalNumInchi":687,"MappedInchi":119,"MetexploreIdMapping":1760},{"idMysql":1899,"type":"biocyc","orgName":"Vibrio cholerae","strain":"O1 biovar eltor str. N16961","nameBioSource":"Vcho","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":682,"MappedInchi":78,"MetexploreIdMapping":1761},{"idMysql":1978,"type":"biocyc","orgName":"Vitis vinifera","strain":"","nameBioSource":"GRAPE","source":"PlantCyc","version":"08-07-2014","TotalNumInchi":1246,"MappedInchi":73,"MetexploreIdMapping":1762},{"idMysql":1756,"type":"biocyc","orgName":"Xanthomonas campestris","strain":"pv. campestris str. B100","nameBioSource":"Xb100","source":"BioCyc","version":"18.0","TotalNumInchi":1538,"MappedInchi":156,"MetexploreIdMapping":1763},{"idMysql":1904,"type":"biocyc","orgName":"Xylella fastidiosa","strain":"9a5c","nameBioSource":"Xfas","source":"MicroCyc","version":"08-07-2014","TotalNumInchi":557,"MappedInchi":74,"MetexploreIdMapping":1764},{"idMysql":1977,"type":"biocyc","orgName":"Zea mays","strain":"mays","nameBioSource":"CORN","source":"PlantCyc","version":"08-07-2014","TotalNumInchi":1278,"MappedInchi":80,"MetexploreIdMapping":1765}]
	# json_data.close()
	return render(request, 'polyomics_chemical_library.html', {"home": True, "metexplore_info": data1})

# TEMPORARY VIEWS, HAVE TO BE MOVED FOR END USAGE 
def result(request):
	return render(request, 'base_result.html')

# def get_scan_data(mzxmlFile, rt):
# 	xcms = importr("xcms")
# 	file = xcms.xcmsRaw(mzxmlFile.file.path)
# 	time = [str(i) for i in list(file.do_slot("scantime"))]
# 	index = time.index(str(rt))
# 	scan = xcms.getScan(file, index+1)
# 	# for i in range(len(scan)):
# 	# 	print scan[i]
# 	mass = list(scan.rx(True, 1))
# 	# print mass
# 	print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
# 	# print type(scan)
# 	intensity = list(scan.rx(True, 2))
# 	# print intensity
# 	lineList = []
# 	for i in range(len(intensity)):
# 		lineList.append([float(mass[i]),intensity[i]])
# 	return lineList
# 	# print "index : ",index


def get_peaks(request):
	if request.is_ajax():
		ppm = int(request.GET['ppm'])
		rtWindow = int(request.GET['rtwindow'])
		peak_id = request.GET['id']
		polarity = request.GET['polarity']
		rt = float(request.GET['rt'])
		mass = float(request.GET['mass'])
		print "peak id",peak_id
		print polarity
		print rt
		print mass
		massWindow = mass * ppm * 0.000001
		print "after mass window"
		massUp = mass + massWindow
		massLow = mass - massWindow
		rtUp = rt + rtWindow/2
		rtLow = rt - rtWindow/2
		print "after rtLow"
		u = robjects.FloatVector([massLow,massUp])
		mzrange = robjects.r['matrix'](u, ncol = 2)
		w = robjects.FloatVector([rtLow,rtUp])
		rtrange = robjects.r['matrix'](w, ncol = 2)
		xcms = importr("xcms")
		sample_ids = [560,561,562,563,564,565,566,567,568]
		data = []
		for sample_id in sample_ids:
			name = Sample.objects.get(id=sample_id).name.split(".")[0]
			print "name: ",name
			if polarity == "negative":
				mzxmlfile = Sample.objects.get(id=sample_id).samplefile.negdata
			else:
				mzxmlfile = Sample.objects.get(id=sample_id).samplefile.posdata
			file = xcms.xcmsRaw(mzxmlfile.file.path)
			print "file opened"
			print "mzrange: ",mzrange
			print "rtrange: ",rtrange
			y = xcms.rawMat(file,mzrange, rtrange)
			# print "Y : ",y
			lineList = []
			try:
				time = list(y.rx(True, 1))
				# print "time"
				intensity = list(y.rx(True, 3))
				for i in range(len(intensity)):
					lineList.append([float(time[i]),round(float(intensity[i]), 3)])
			except:
				lineList = None
				print "EXCEPTION TRIGGERED!!!!!"
			# print lineList
			data.append([name,lineList])
				# print data
		message = "got somthing on the server!!!"
		response = simplejson.dumps(data)
		return HttpResponse(response, mimetype='application/json')
		# if polarity == "NEG":
		# 	mzxmlfile = Sample.objects.get(id=sample_id).samplefile.negdata
		# else:
		# 	mzxmlfile = Sample.objects.get(id=sample_id).samplefile.posdata
		# data = get_scan_data(mzxmlfile, rt)
		# print "my polarity : ",polarity
		# print "my sample id : ",sample_id
		# print "my retention time : ",rt
		# message = "my sample id on the server side is : " + str(sample_id)
		# response = simplejson.dumps(data)
		# return HttpResponse(response, mimetype='application/json')
