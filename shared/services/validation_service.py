import sys, re, datetime
from functools import wraps
from flask import request, render_template

def str_to_class(classname):
    return getattr(sys.modules["builtins"], classname)

def generate_missing_error(args: list):
    return f"Missing arguments: {', '.join(args)}"

def validate_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = request.form.get('username')
        password = request.form.get('password')
        if username is None or password is None or username == "" or password == "":
            return render_template('login.html', message="Invalid username or password"), 401
        return f(*args, **kwargs)
    return decorated_function

def validate_john_trigger(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        appliance_id = request.form.get('appliance_id')
        status = request.form.get('status')
        if appliance_id is None or status is None or appliance_id == "" or status == "":
            return generate_missing_error(["appliance_id", "status"]), 400
        return f(*args, **kwargs)
    return decorated_function

def validate_john_aircon_temp(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        appliance_id = request.form.get('appliance_id')
        value = request.form.get('value')
        appliance_id_invalid = appliance_id is None or appliance_id == ""
        value_invalid = value is None or value == ""
        if (appliance_id_invalid or value_invalid):
            missing = []
            if appliance_id_invalid:
                missing.append("appliance_id")
            if value_invalid:
                missing.append("value")
            return generate_missing_error(missing), 400
        try:
            appliance_id = int(appliance_id)
            if appliance_id not in [4, 5]:
                raise Exception()
        except:
            return "Invalid appliance id", 400
        return f(*args, **kwargs)
    return decorated_function

def validate_john_month_year(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        month = request.form.get('month')
        year = request.form.get('year')
        month_invalid = month is None or month == ""
        year_invalid = year is None or year == ""
        if (month_invalid or year_invalid):
            missing = []
            if month_invalid:
                missing.append("month")
            if year_invalid:
                missing.append("year")
            return generate_missing_error(missing), 400
        try:
            month = int(month)
            year = int(year)
            if month < 1 or month > 12 or year < 0:
                raise Exception()
        except:
            return "Invalid month or year", 400
        return f(*args, **kwargs)
    return decorated_function

def validate_timmy_settings(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        door_height = request.form.get('door-height')
        in_distance_threshold = request.form.get('in-distance-threshold')
        out_distance_threshold = request.form.get('out-distance-threshold')
        closing_duration = request.form.get('closing-duration')
        detection_duration = request.form.get('detection-duration')
        face_detection_duration = request.form.get('face-detection-duration')
        door_height_invalid = door_height is None or door_height == ""
        in_distance_threshold_invalid = in_distance_threshold is None or in_distance_threshold == ""
        out_distance_threshold_invalid = out_distance_threshold is None or out_distance_threshold == ""
        closing_duration_invalid = closing_duration is None or closing_duration == ""
        detection_duration_invalid = detection_duration is None or detection_duration == ""
        face_detection_duration_invalid = face_detection_duration is None or face_detection_duration == ""
        if (door_height_invalid or in_distance_threshold_invalid or out_distance_threshold_invalid or closing_duration_invalid or detection_duration_invalid or face_detection_duration_invalid):
            missing = []
            if door_height_invalid:
                missing.append("door-height")
            if in_distance_threshold_invalid:
                missing.append("in-distance-threshold")
            if out_distance_threshold_invalid:
                missing.append("out-distance-threshold")
            if closing_duration_invalid:
                missing.append("closing-duration")
            if detection_duration_invalid:
                missing.append("detection-duration")
            if face_detection_duration_invalid:
                missing.append("face-detection-duration")
            return generate_missing_error(missing), 400
        try:
            door_height = int(door_height)
            in_distance_threshold = int(in_distance_threshold)
            out_distance_threshold = int(out_distance_threshold)
            closing_duration = int(closing_duration)
            detection_duration = int(detection_duration)
            face_detection_duration = int(face_detection_duration)
        except:
            return "Invalid settings", 400
        return f(*args, **kwargs)
    return decorated_function

def validate_timmy_profile(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        birthday = request.form.get('birthday')
        height = request.form.get('height')
        weight = request.form.get('weight')
        birthday_invalid = birthday is None or birthday == ""
        height_invalid = height is None or height == ""
        weight_invalid = weight is None or weight == ""
        if (birthday_invalid or height_invalid or weight_invalid):
            missing = []
            if birthday_invalid:
                missing.append("birthday")
            if height_invalid:
                missing.append("height")
            if weight_invalid:
                missing.append("weight")
            return generate_missing_error(missing), 400
        try:
            birthday = datetime.datetime.strptime(birthday, "%Y-%m-%d")
            height = int(height)
            weight = int(weight)
        except:
            return "Invalid birthday, height or weight", 400
        return f(*args, **kwargs)
    return decorated_function

def validate_iata_region(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        iata_region = request.form.get('iata_region')
        iata_region_invalid = iata_region is None or iata_region == ""
        if (iata_region_invalid):
            return generate_missing_error(["iata_region"]), 400
        if (iata_region not in ["RAI","CPT","JNB","ALG","AAE","CZL","ORN","BUG","CAB","LAD","COO","FRW","GBE","MUB","PKW","BOY","OUA","SID","BBY","BGU","BGF","BBT","IRO","BIV","CRF","ODA","AEH","MQQ","NDJ","AJN","HAH","YVA","BZV","PNR","FIH","LIQ","ASK","JIB","AUE","ABS","AAC","AAC","ALY","ATZ","ASW","HBH","CAI","EMY","HRG","UVL","LXR","MUH","UVL","PSD","SKV","SSH","SEW","SSG","ADD","LBQ","LBV","MFF","MJL","MVB","POG","UVE","BJL","ACC","ABJ","BYK","DJO","HGO","MJC","SPY","ZSS","MYD","MBA","NBO","MSU","MLW","ROB","BEN","SEB","TIP","TNR","MJN","BLZ","LLW","BKO","NDB","NKC","OUZ","DZA","AGA","AHU","CAS","CMN","FEZ","RAK","OZZ","OUD","RBA","TNG","BEW","MPM","MPA","KMP","LUD","OKU","OND","OMD","NDU","SWP","TSB","ERS","WDH","AJY","RLT","MFQ","NIM","ZND","ABV","KAN","LOS","PHC","RUN","KGL","TMS","DKR","SEZ","FNA","MGQ","AGZ","ALJ","ADY","BFN","DUR","ELS","ELL","GRJ","KIM","KLZ","HLA","LUJ","MGH","MEZ","MBM","MZF","NLP","NCS","OUH","PHW","PZB","PTG","NTY","PBZ","PLZ","PRY","RCB","SIS","SZK","SBU","TCU","ULD","UTT","UTN","VYD","WVB","WEL","KSL","KRT","PBM","MTS","ARK","DAR","JRO","DJE","MIR","SFA","TUN","EBB","ULU","FKI","FBM","CIP","KIW","LUN","MFU","NLA","BFO","BUQ","GWE","HRE","HWN","MVZ","SAY","VFA","SPK","OKD","HKG","UKB","UKY","NGO","TYO","HND","NRT","MLE","KTM","ICN","SEL","CMB","BZL","CGP","DAC","ZYL","PBH","PEK","NAY","SHA","PVG","TSN","XMN","DGM","CAN","SZX","NNG","HRB","ZJK","WUH","AMD","ATQ","QNB","IXB","BLR","BDQ","IXG","BHO","BBI","BOM","CCU","CCJ","IXC","MAA","COK","CJB","DEL","GOI","GAU","HYD","JAI","JLR","IXW","QJU","CCU","LKO","MAA","NAG","PAT","PNQ","RAJ","IXR","SXR","STV","TRV","TRZ","VNS","AXT","ASJ","AOJ","KMQ","QCB","CTS","FUK","FKS","HAC","HKD","HIJ","LSG","KOJ","KCZ","KMJ","KUH","MMJ","MYJ","MMY","HNA","KMI","NGS","KIJ","OIT","OKJ","OKA","OSA","ITM","KIX","SDS","CTS","SDJ","TAK","TKS","TOY","GAJ","YOK","CGQ","ADX","ALA","TSE","ICN","DLC","SHE","MFM","MRU","RRG","ULN","XIY","TNA","TAO","TYN","CTU","CKG","QPG","SIN","PUS","DYU","KHH","MZG","TPE","TAY","SKD","TAS","TMZ","URC","HGH","PTP","BON","CUR","SXM","NEV","SKB","UVF","SLU","SFG","SVD","HAV","HOG","SCU","VRA","LRM","POP","PUJ","SDQ","PAP","KIN","MBJ","FDF","BQN","MAZ","PSE","SJU","TAB","POS","STX","STT","EIS","VIJ","EIS","FPO","NAS","GCM","AXA","ANU","AUA","CCZ","GHB","GBI","MHH","ELH","RSD","ZSA","TCB","BGI","BDA","PTY","SJO","SAL","RTB","SAP","SDH","TGU","BZE","GUA","MGA","SJJ","SOF","NAN","SUV","SUV","BUD","SKP","BUH","OTP","EVN","BAK","MSQ","OMO","BOJ","GOZ","ROU","SLS","TGV","VAR","VID","DBV","LSZ","OSI","PUY","RJK","SPU","ZAD","ZAG","QUF","TLL","TBS","RIX","VNO","OHD","CND","AER","KHV","HTA","IKT","KZN","MRV","MOW","DME","SVO","VKO","MMK","OVB","LED","UUD","VLU","ARH","YKS","BTS","LJU","MBX","KBP","IEV","LWO","NLV","ODS","SIP","BEG","INI","QND","TGD","PRN","TIV","TIA","INN","SZG","VIE","CPH","HEL","BER","SXF","TXL","DRS","HAM","ATH","HEW","CFU","KGS","JMK","MJT","RHO","SKG","IBZ","ORK","DUB","GWY","KIR","NOC","SNN","CAG","MLA","BGO","OSL","TRF","KRK","WAW","LIS","PDL","PMI","SVQ","VLC","GOT","STO","ARN","BMA","BHD","BFS","PIK","GLA","INV","ALV","GRZ","KLU","LNZ","ANR","BRU","LGG","AKT","LCA","QLI","NIC","PFO","PRG","AAR","AAL","BLL","EBJ","FAE","KRP","ODE","RNN","SKS","SGD","TED","ENF","IVL","JOE","JYV","KAJ","KHJ","KEM","KTT","KOK","KUO","KAO","LPP","MHQ","MIK","OUL","POR","RVN","SVL","SJY","SOT","TMP","TKU","VAA","VRK","AJA","LBI","NCY","AUR","BIA","BIQ","BOD","BES","CLY","CMF","CFE","DNR","FSC","FRJ","GNB","LRH","LAI","LIL","LIG","LRT","LDE","LYS","MRS","MZM","MPL","MLH","ENC","NTE","NCE","FNI","PAR","CDG","LBG","ORY","PUF","PGF","UIP","RNS","RNE","RDZ","SBK","EBU","SXB","TLS","AGB","BYU","BRE","CGN","DTM","DUS","ERF","FRA","HNN","FDH","HAJ","HOQ","FKB","KEL","CGN","LEJ","MUC","FMO","MSR","NUE","PAD","SCN","STR","GWT","WIE","GIB","GPA","CHQ","JKH","HER","KLX","AOK","KVA","PVK","SKG","SMI","JSI","JTR","ZTH","CXI","EGS","REK","KEF","SXL","AHO","AOI","BRI","BGY","BLQ","VBS","BDS","CTA","FLR","GOA","SUF","LMP","MIL","LIN","MXP","BGY","NAP","OLB","PMO","PNL","PEG","PSR","PSA","REG","RMI","ROM","CIA","FCO","TPS","TSF","TRS","TRN","VCE","VBS","VRN","LUX","AMS","HAG","EIN","LEY","MST","RTM","AES","ALF","BDU","BOO","BNN","EVE","FRO","HFT","HAU","KKN","KRS","KSU","LKL","SOG","SVG","TOS","TRD","GDN","POZ","SZZ","FAO","FNC","HOR","OPO","PXO","SMA","TER","ALC","LEI","ACE","BJZ","BCN","BIO","ODB","FUE","GRO","GRX","XRY","LCG","LPA","MAD","MAH","AGP","MJV","OVD","REU","EAS","SPC","SDR","SCQ","TCI","TFS","TFN","VLL","VDE","VGO","VIT","ZAZ","LYR","JHE","JKG","KLR","KSD","KRN","KID","LDK","LLA","MMA","MMX","NRK","ORB","RNB","SDL","VXO","VST","VBY","ACH","BSL","BRN","ZDJ","GVA","LUG","ZRH","EAP","TFN","TFS","SZD","ABZ","BHX","BRS","CBG","CWL","EMA","LDY","EDI","GCI","HUY","IOM","JER","LBA","LPL","LON","LCY","LGW","LHR","LTN","STN","MAN","NCL","KOI","SOU","SEN","STN","SYY","LSI","MME","WIC","JRS","TLV","BEY","IST","IZM","KBL","BAH","ABD","THR","BGW","SDA","BSR","KIK","OSM","ETH","VDA","HFA","AMM","ADJ","AQJ","KWI","GJN","MCT","SLL","BHV","BNP","CJL","DSK","LYP","GIL","GWD","HDD","ISB","JAG","JIW","KHI","KDD","OHT","LHE","MWD","QML","MJD","MUX","MFG","WNS","PJG","PSI","PEW","UET","RYK","RAZ","RWP","SDT","MPD","KDU","SUL","SKZ","TUK","PZH","DOH","ADA","ANK","AYT","DLM","ASB","AUH","FJR","DXB","RKT","SHJ","AAN","FJR","DHA","JED","AHB","MED","MED","RUH","TUU","TIF","YNB","DMM","ALP","DAM","ADE","SAH","YAT","YVB","YYC","YCB","YYQ","CFG","YDF","YEA","YEG","YXD","YFO","YFA","YMM","YSM","YXJ","YFC","YQX","YGX","YYR","YHZ","YUX","YHM","YHR","YEV","YFB","ZKE","YLW","YVP","YGW","XLB","YGL","YLR","YXU","YQM","YMQ","YUL","YMX","YSR","YVQ","YOW","YPN","YXS","YPR","XPK","YQB","YOP","YQR","YRB","YSJ","YZP","YXE","ZTM","YYD","XSI","YIF","YYT","FSP","YXT","YQD","YTH","YQT","YTZ","YYZ","YTO","YVO","YVR","YYJ","YWK","YXN","YXY","YQG","YWG","YZF","UAK","SFJ","ACA","AGU","CUN","CZA","CUU","CME","CJS","CEN","CVM","CLQ","CZM","CUL","GDL","HMO","HUX","ZIH","LAP","LZC","BJX","LTO","SJD","LMM","ZLO","MZT","MID","MXL","MEX","MEX","MTT","MTY","NTR","MLM","NLD","OAX","PBC","PXM","PVR","SJD","SLP","SRL","TAM","TIJ","TGZ","VER","VSA","ZCL","ABR","ABI","CAK","ABY","ALB","ABQ","ESF","ABE","AOO","AMA","ANC","ARB","ANB","ATW","AVL","ASE","AHN","ATO","ATL","ACY","AGS","AUG","AUS","BFL","BWI","BGR","BTR","BPT","BKW","BLI","BJI","BEH","BET","BIL","BHM","BIS","BMI","BMG","BLF","BOI","BXS","BOS","BZN","BFD","BRD","BDR","BKX","BQK","BUF","BHC","BUR","BRL","BTV","BTM","CLD","CPR","CDC","CID","CMI","CHS","CRW","CLT","CHO","CHA","CYS","MDW","ORD","CHI","CIC","CVG","CKB","BKL","CLE","COD","KCC","CLL","COS","CAE","CSG","CMH","CCR","CDV","CRP","CGA","CEC","DAL","DFW","DAN","DAY","DAB","DEC","DEN","DSM","DET","DTW","DTT","DVL","DLG","DHN","DUJ","DBQ","DLH","DRO","DUT","EAU","ELP","EKI","EKO","ELM","ELY","ERI","ESC","EUG","ACV","EVV","FAI","FAR","FMN","FYV","FAY","FLG","FNT","FLO","FOD","FHU","FLL","FMY","RSW","FSM","VPS","FWA","FKL","FAT","GAD","GNV","GCC","GGW","GDV","GCN","GFK","GJT","GRR","GPZ","GTF","GRB","LWB","GSO","GLH","PGV","GSP","GON","GPT","GUC","HNS","CMX","HRL","HAR","MDT","BDL","HVR","HLN","HIB","HKY","ITO","HHH","HOM","HNL","HNH","HOU","IAH","HTS","HSV","HON","HYA","HYG","IDA","ILI","IPL","IND","INL","IYK","ITH","JAC","JXN","JAN","MKL","JAX","OAJ","JMS","JHW","JST","JLN","JNU","OGG","AZO","FCA","MUE","MCI","JHM","MKK","ENA","KTN","EYW","ILE","AKN","ISO","LMT","KLW","TYS","ADQ","KOA","OTZ","WLB","LSE","LAF","LFT","LCH","HII","TVL","LNY","LNS","LAN","LAR","LRD","LAS","LBE","PIB","LAW","LEB","LWS","LWT","LEX","LIH","LNK","LIT","LGB","LIJ","ISP","GGG","LAX","SDF","LBB","LYH","MCN","MSN","MHT","MTH","MQT","MVY","MCW","MTO","MFE","MFR","MLB","MEM","MCE","MEI","MTM","MIA","MAF","MLS","MKE","MSP","MOT","MSO","MHE","MOB","MOD","MLI","MLU","MRY","MGM","MTJ","MGW","MWH","MCL","MSL","MKG","MYR","ACK","APF","BNA","EWN","HVN","MSY","JFK","LGA","EWR","NYC","SWF","PHF","IAG","OME","ORF","OTH","OAK","OKC","OMA","ONT","SNA","ORL","OSH","OWB","OXR","PAH","PGA","PKB","PSP","PMD","PFN","PSC","PLN","PDT","PNS","PIA","PSG","PHL","PHX","PIR","PIT","PLB","PIH","CLM","PWM","PDX","POU","PQI","PVD","SCC","PUB","PUW","UIN","RDU","RAP","RDG","RDD","RDM","RNO","RHI","RIC","ROA","RST","ROC","RKS","RFD","RKD","RWI","SMF","MBS","SLE","SNS","SBY","SLC","SJT","SAT","SAN","SFO","SJC","SBP","SBA","SMX","STS","SRQ","SAV","SCF","SEA","SHD","SHR","SHV","SDY","SUX","FSD","SIT","SGY","SBN","GEG","SPI","SGF","SGU","STL","SCE","HDN","SCK","SUN","SYR","TKA","TLH","TPA","TEX","HUF","TXK","TVF","KTB","TOL","TVC","TTN","TRI","TUS","TUP","TUL","TCL","TWF","TYR","UCA","EGE","VDZ","VLD","VEL","VRB","VIS","ACT","ALW","BWI","IAD","DCA","WAS","ALO","ATY","CWA","EAT","PBI","WYS","HPN","SPS","ICT","AVP","IPT","ISL","ILM","OLF","ORH","WRL","WRG","YKM","YAK","YUM","ORL","AEP","BAQ","BUE","CTG","EZE","IGR","IPC","LIM","MVD","SCL","UIO","LPB","SRZ","PUQ","VAP","BOG","BGA","IQT","COR","MDQ","MDZ","ROS","SLA","BRC","RSA","CBB","SRB","GIG","SDU","RIO","SAO","CGH","GRU","VCP","AJU","BEL","CNF","BVB","BSB","CGR","CGB","CWB","FLN","FOR","GYN","GRU","JCB","JPA","MCP","MCZ","MAO","QGF","NAT","POA","PVH","REC","RBR","SSA","SRA","SLZ","THE","UDI","VIX","CLO","MDE","AXS","PEI","ADZ","SSL","GYE","SNC","CAY","CKY","LEK","BXO","GEO","ASU","BLA","CCS","MAR","PMV","PZO","VLN","ASP","AYQ","PER","BOB","PPT","PPG","ADL","ALH","ABX","AYR","BNK","ABM","BLT","ZBO","BMP","BNE","BHQ","BME","BDB","BWT","CNS","CBR","CVQ","CSI","CED","CES","CXT","CMQ","CFS","KCE","CPD","CTN","OOM","DBY","DRW","DDI","DRB","DPO","DBO","DKI","DYA","EDR","EMD","EPR","GEX","GET","GLT","OOL","GOO","GOV","GKL","GFF","GTE","GTI","GYP","HLT","HTI","HIS","HVB","HNK","HBA","HMH","IGH","IFL","KGI","KTA","KRB","KTR","KGC","KWM","KNX","LST","LVO","LEA","LER","LNO","LDC","LSY","LZR","IRG","LRE","MKY","MTL","MBH","MKR","MEL","MIM","MMM","MQL","MOV","MRZ","MGB","MMG","ISA","NAA","NRA","BEO","NTL","ZNE","NSA","NLK","OLP","OAG","ORS","PBO","PUG","PHE","PTJ","PLO","PQQ","PPP","UEE","ROK","NSO","JHQ","SIX","SOI","KBY","MCY","SYD","TMW","TRO","TEM","TCA","TIS","TPR","TWB","TSV","WGA","WMB","WEI","HAP","WYA","WHM","WUN","WOL","UMR","WYN","HUH","XMH","MAU","MOZ","RFP","RGI","GND","SUM","GUM","RAR","KNS","LIF","PNI","ILP","IOU","MEE","NOU","TOU","SPN","APW","GSI","HIR","VLI","SON","FUT","WLS","AKL","BHE","CHC","DUD","IVC","IVC","MFN","GTN","NSN","PMR","ZQN","ROT","TEU","WLG","WHK","WRE","LFW","TBU","PNH","VTE","RGN","RGN","BWN","KUB","BJM","DLA","GOU","MVR","NGE","YAO","DPS","HLP","JKT","CGK","MES","MDC","SUB","TOD","UPG","BTU","JHB","BKI","KUL","SZB","KUA","KCH","LBU","LGK","MYY","PEN","SBW","TWU","LAE","MFO","POM","CBU","NOP","MNL","BKK","CNX","HDY","PYX","HKT","UTP","HAN","SGN","HUI","SGN"]):
            return "Invalid iata_region", 400
        return f(*args, **kwargs)
    return decorated_function