import re

def explicit_ids(query):
    return set(int(x) for x in re.findall(r'(?:보고서\s*(?:번호\s*)?#?\s*|RPT-|report\s*(?:id\s*)?#?\s*)([0-9]+)',query,re.I) if 0<int(x)<=9223372036854775807)
