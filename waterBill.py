import shutil
import os
import glob
from selenium import webdriver
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO


# copied from online
def convert_pdf_to_txt(path, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)
    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(path, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close()
    return text


# set some path's, obviously differently for every computer and where you want the file to go
path = 'C:/Users/Artic/Desktop/Water'
pdfPath = 'C:/Users/Artic/PycharmProjects/waterBill/example.pdf'

# delete a directory for water on the desktop, then create one, or just create one if there wasn't one to begin with
try:
    shutil.rmtree(path)
    os.makedirs(path)
except FileNotFoundError:
    os.makedirs(path)

try:
    os.remove('water.txt')
except Exception:
    pass

# start logging in using selenium
ch_options = webdriver.ChromeOptions()

# set default download area as the path you want
pref = {"download.default_directory": r"C:\Users\Artic\Desktop\Water"}
ch_options.add_experimental_option("prefs", pref)
browser = webdriver.Chrome(options=ch_options)

# save username, passwords and securiy question info right here
usernameStr = 'username'
passwordStr = 'password'
boss = 'secQ1'
food = 'secQ2'
restaurant = 'secQ3'

# open up the water page, and start logging in
browser.get('https://secure8.i-doxs.net/CityOfPhiladelphiaWRB/SignIn.aspx')
username = browser.find_element_by_id('main_UID')
username.send_keys(usernameStr)
password = browser.find_element_by_id('main_PWD')
password.send_keys(passwordStr)
signInButton = browser.find_element_by_id('main_btnSubmit')
signInButton.click()

# check to see which security question pops up and answer it based off the question
# if you want to try this, change the security question to what your security questions are
sec = browser.find_element_by_id('main_txtAnswer')
securityAns = browser.find_element_by_id('main_lblQuestion').text
if securityAns == "Your favorite restaurant?":
    sec.send_keys(restaurant)
elif securityAns == "Your favorite food?":
    sec.send_keys(food)
else:
    sec.send_keys(boss)

# navigate to the bills section
contButton = browser.find_element_by_id('main_btnSubmit')
contButton.click()
billsButton = browser.find_element_by_id('lnkBills')
billsButton.click()

# store the drop down options
options = [x for x in browser.find_elements_by_tag_name("option")]
optLen = (len(options))
addrList = []
dateList = []

# for every option/address that were trying to download the water bill for,
# download it

#for element in range(optLen - 1):  # final drop down option is empty, so we have to have one less than the len of it
for element in range(0,10):
    optionList = browser.find_elements_by_tag_name("option")
    # append the address to a list so that we can rename these files later using this list as the naming list
    addrList.append(optionList[element].text)
    print(optionList[element].text + str(element))
    optionList[element].click()
    # press the refresh button to get the bills for the selected address
    refresh = browser.find_element_by_id('main_imgbtnUpdateServiceAddress')
    refresh.click()
    date = browser.find_element_by_class_name('jqBillPeriod')
    dateList.append(date.text)
    bill = browser.find_element_by_id('main_rptBills_lnkBills_0')
    bill.click()
    download = browser.find_element_by_id('PDF')
    download.click()
    # an alert shows up to warn us of something, so we gotta say ok to it
    alert = browser.switch_to.alert
    alert.accept()
    # go to the next option
    home = browser.find_element_by_id('lnkToHome')
    home.click()

# sort files based on their creation time so we can rename the files correctly
files = glob.glob('C:/Users/Artic/Desktop/Water/*')
files.sort(key=os.path.getctime)

dataList = []
# rename these files based on the list we had created earlier
for count, filename in enumerate(files):
    dst = path + '/' + addrList[count] + str(count) + ".pdf"
    os.rename(filename, dst)
    # grab the data from the pdf
    textList = convert_pdf_to_txt(dst, pages=[0])
    textList = textList.replace('$', '\n$')
    linedTextList = textList.split('\n')
    dataList.append(addrList[count] + " " + dateList[count] + " " + linedTextList[len(linedTextList) - 5])

# sort the given list
dataList = sorted(dataList)
for i in range(len(dataList)):
    with open('water.txt', mode='a', encoding='utf-8') as f:
        f.write(dataList[i] + "\n")

