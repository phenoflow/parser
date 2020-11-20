# rest, 2020.

import sys, csv, requests, json
from html.parser import HTMLParser
from html.entities import name2codepoint

def identifyCodes(dynamicCodes):
    staticCodes = ["F527.", "F520.", "XE2QD", "Y20ff"];
    codes = staticCodes + dynamicCodes;
    with open(sys.argv[1], 'r') as file_in, open('otitis-potential-cases.csv', 'w', newline='') as file_out:
        csv_reader = csv.DictReader(file_in)
        csv_writer = csv.DictWriter(file_out, csv_reader.fieldnames + ["ctv3-identified"])
        csv_writer.writeheader();
        for row in csv_reader:
            newRow = row.copy();
            for cell in row:
                if ([value for value in row[cell].split(",") if value in codes]):
                    newRow["ctv3-identified"] = "CASE";
                    break;
                else:
                    newRow["ctv3-identified"] = "UNK";
            csv_writer.writerow(newRow);

class UMLSParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if(attr[0]=="action"):
                tgt = attr[1].rsplit('/', 1)[-1];
                r = requests.post("https://utslogin.nlm.nih.gov/cas/v1/tickets/" + tgt, data={"service":"http://umlsks.nlm.nih.gov"})
                ticket = r.content.decode("utf-8");
                r = requests.get("https://uts-ws.nlm.nih.gov/rest/search/current?string=otitis&sabs=RCD,SNOMEDCT_US&returnIdType=code&includeObsolete=true&ticket=" + ticket);
                umlsCodes = [result["ui"] for result in json.loads(r.content.decode("utf-8"))["result"]["results"]]
                identifyCodes(umlsCodes);

parser = UMLSParser()

API_KEY="";
r = requests.post("https://utslogin.nlm.nih.gov/cas/v1/api-key", data={"apikey":API_KEY})
if(r.status_code==201): parser.feed(str(r.content));
else: identifyCodes([]);
