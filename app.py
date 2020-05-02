from flask import Flask, render_template, request, redirect, url_for, jsonify
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from pprint import pprint as print
from gensim.summarization.summarizer import summarize
from gensim.summarization import keywords
import nltk
import re
# nltk.download('all')
import pandas as pd
import matplotlib.pyplot as py
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json

cd = ''
company_name = ''
ds = ''
company = ''
news2 = []
headlines = []
app = Flask(__name__)


# Ratios
ratio = [
    {'name': 'Basic EPS',
     'data': [45, 46, 47, 48, 49, 37, 56, 60, 31, 50],
     'graph': '#chart1'
     },
    {'name': 'Diluted EPS',
        'data': [45, 46, 47, 48, 49, 37, 56, 60, 31, 23],
        'graph': '#chart1'
     },
    {'name': 'Book Value',
        'data': [45, 46, 47, 48, 49, 37, 56, 60, 31, 23],
        'graph': '#chart1'
     },
    {'name': 'Divident/Share',
        'data': [45, 46, 47, 48, 49, 37, 56, 60, 31, 23],
        'graph': '#chart1'
     },
    {'name': 'PBDIT Margin(%)',
        'data': [45, 46, 47, 48, 49, 37, 56, 60, 31, 23]
     },
    {'name': 'Net Profit Margin(%)',
        'data': [45, 46, 47, 48, 49, 37, 56, 60, 31, 23]
     },
    {'name': 'Return on Networth/Equity(%)',
        'data': [45, 46, 47, 48, 49, 37, 56, 60, 31, 23]
     },
    {'name': 'Return on Capital Employed(%)',
        'data': [45, 46, 47, 48, 49, 37, 56, 60, 31, 23]
     },
    {'name': 'Return on Assets',
        'data': [45, 46, 47, 48, 49, 37, 56, 60, 31, 23]
     },
    {'name': 'Total Debt/Equity(X)',
        'data': [45, 46, 47, 48, 49, 37, 56, 60, 31, 23]
     },
    {'name': 'Asset Turnover Ratio(%)',
        'data': [45, 46, 47, 48, 49, 37, 56, 60, 31, 23]
     },
    {'name': 'Current Raito(X)',
        'data': [45, 46, 47, 48, 49, 37, 56, 60, 31, 23]
     },
    {'name': 'Quick Ratio(X)',
        'data': [45, 46, 47, 48, 49, 37, 56, 60, 31, 23]
     },
    {'name': 'Divident Payout Ratio(NP)(%)',
        'data': [45, 46, 47, 48, 49, 37, 56, 60, 31, 23]
     },
    {'name': 'Earnings Yield',
        'data': [45, 46, 47, 48, 49, 37, 56, 60, 31, 23]
     }
]

# speeches

newsLinks = []




@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    global user
    global driver
    global company_name
    global cd
    global company

    if request.method == 'POST':
        user = request.form['nm']
        driver = Chrome(executable_path='C:/chromedriver')
        driver.get("https://www.moneycontrol.com/")
        driver.implicitly_wait(10)
        driver.find_element_by_xpath(
            "//input[@id='search_str']").send_keys(user + "\n")
        elems = driver.find_elements_by_xpath("//a[@href='#sec_finanl']")
        driver.implicitly_wait(10)
        for elem in elems:
            links = elem.get_attribute("href")
            # print(links)
        driver.implicitly_wait(10)
        links = links[::-1]
        code = re.search('#(.+?)/', links).group(1)
        # print (code[::-1])
        cd = code[::-1]
        cn = re.search('/(.+?)/', links).group(1)
        # print (cn[::-3])
        company_name = cn[::-1]
        links = links[::-1]
        driver.get(links)
        company = driver.find_element_by_xpath('//h1[@class="pcstname"]').text
        return render_template('stats.html', usr=company)
    else:
        return render_template('login.html')

@app.route('/ratios')
def ratios():
    url1 = "https://www.moneycontrol.com/financials/" + \
        company_name+"/ratiosVI/"+cd+"/1#"+cd
    url2 = "https://www.moneycontrol.com/financials/" + \
        company_name+"/ratiosVI/"+cd+"/2#"+cd
    ratios1 = pd.read_html(url1, header=0)[0]
    ratios2 = pd.read_html(url2, header=0)[0]
    ratios1 = ratios1.dropna(how='all', axis=1)
    ratios1 = ratios1.dropna(how='any', axis=0)
    ratios2 = ratios2.dropna(how='all', axis=1)
    ratios2 = ratios2.dropna(how='any', axis=0)
    columns = ratios1.columns.tolist()
    columns = columns[::-1]
    ratios1 = ratios1[columns]
    columns = [columns[-1]] + columns[:-1]
    ratios1 = ratios1[columns]
    columns = ratios2.columns.tolist()
    columns = columns[::-1]
    ratios2 = ratios2[columns]
    columns = [columns[-1]] + columns[:-1]
    ratios2 = ratios2[columns]
    ratios2.drop(ratios2.columns[0], axis=1, inplace=True)
    ratio = pd.concat([ratios2, ratios1], axis=1, sort=False)
    ratio.set_index(ratio.columns[5], inplace=True)
    ratio_list = list(['Basic EPS (Rs.)', 'Diluted EPS (Rs.)', 'Book Value [ExclRevalReserve]/Share (Rs.)', 'Dividend / Share(Rs.)', 'PBIT Margin (%)', 'Net Profit Margin (%)', 'Return on Networth / Equity (%)',
                       'Return on Capital Employed (%)', 'Return on Assets (%)', 'Total Debt/Equity (X)', 'Asset Turnover Ratio (%)', 'Current Ratio (X)', 'Quick Ratio (X)', 'Dividend Payout Ratio (NP) (%)', 'Earnings Yield'])
    ratio_final = ratio.loc[ratio_list]
    ratio_format = []
    for ratio in ratio_list:
        values = list(ratio_final.loc[ratio])
        # print(values)
        ratio_format.append(
            {'name': ratio, 'data': values, 'graph': '#chart1'})
    ratio_json = json.dumps(ratio_format)
    return ratio_json

@app.route('/speeches')
def get_speech():
    global out
    driver.get("https://www.moneycontrol.com/annual-report/" +
               company_name+"/directors-report/"+cd+"#"+cd)
    
    # director_speech
    director_speech = driver.find_element_by_xpath(
        '//div[@class="report_data"]').text
    director_speech
    d = re.match('.*\\n', director_speech).group()
    # ds = director_speech.rstrip("\n")
    # ds=re.sub('\n',' ',director_speech)
    ds = re.sub(d, ' ', director_speech)

    driver.get("https://www.moneycontrol.com/annual-report/" +
               company_name+"/chairmans-speech/"+cd+"#"+cd)
    chairman_speech = driver.find_element_by_xpath(
        '//div[@class="report_data"]').text
    c = re.match('.*\\n', chairman_speech).group()
    # cs=re.sub('\n',' ',chairman_speech)
    cs = re.sub(c, " ", chairman_speech)

    ds_keyword_list = keywords(ds, words=20, split=True, lemmatize=True)
    cs_keyword_list = keywords(cs, words=20, split=True, lemmatize=True)
    # keywords from whole chairman's speech
    # print(keyword_list)

    ds_keyword_tags = dict(nltk.pos_tag(ds_keyword_list))
    cs_keyword_tags = dict(nltk.pos_tag(cs_keyword_list))

    ds_keywords_final = [
        word for word in ds_keyword_tags.keys() if ds_keyword_tags[word] == 'NN']
    cs_keywords_final = [
        word for word in cs_keyword_tags.keys() if cs_keyword_tags[word] == 'NN']
    # also need to remove company name if there in the list

    # print(keywords_final[:5])
    # summarization
    ds_summ = summarize(ds, word_count=100)
    cs_summ = summarize(cs, word_count=100)

    out = json.dumps([{'summary': cs_summ, 'keywords': cs_keywords_final[:5], 'fullCont':cs}, {
                     'summary': ds_summ, 'keywords': ds_keywords_final[:5], 'fullCont':ds}])
    return out



@app.route('/news')
def news():
    global news_json
    global headlines
    global news2

    driver1= Chrome(executable_path='C:/chromedriver')
    # News
    links2 = []
    driver1.get("https://economictimes.indiatimes.com/")
    WebDriverWait wait = new WebDriverWait(driver1,10)
    wait.until(ExpectedConditions.visibilityOfElementLocated("//input[@class='inputBox']"))
    driver1.find_element_by_xpath("//input[@class='inputBox']").send_keys(company + "\n")

    driver1.find_element_by_xpath(
        "//span[@class='mainSprite news']").click()

    et_news_links = driver1.find_elements_by_xpath(
        "//div[@class='headerText']//a[contains(@href,'')]")

    for elem in et_news_links:
        link = elem.get_attribute("href")
        links2.append(link)

    link_news = links2[0]
    driver1.get(link_news)

    et_news = []
    et = driver1.find_elements_by_xpath(
        "//div[@class='eachStory']//a[contains(@href,'')]")
    for elem in et:
        link = elem.get_attribute("href")
        et_news.append(link)

    et_news = [string for string in et_news if string.endswith(".cms")]

    news_links = et_news[:15]

    headlines = []
    news2 = []
    for link in news_links:
        # annual report
        driver1.get(link)
        headline = driver1.find_element_by_xpath(
            '//h1[@class="clearfix title"]').text
        headlines.append(headline.replace("\n", ""))
        article = driver1.find_element_by_xpath(
            '//div[@class="Normal"]').text
        news2.append(article.replace("\n", ""))

    news_format = []
    for headline, link in zip(headlines, news_links):
        news_dict = {'title': headline, 'link': link}
        news_format.append(news_dict)
    news_json = json.dumps(news_format)

    return news_json

@app.route('/doughnut')
def get_sentiment():

    global name
    analyzer=SentimentIntensityAnalyzer()
    scores=[]
    for x in news2:
        score= analyzer.polarity_scores(x)
        scores.append(score['compound'])
    
    df = pd.DataFrame(list(zip(headlines, news2,scores)), 
                columns =['Headline', 'Article','VADER Score'])     
    mean=df['VADER Score'].mean()
    
    # decide sentiment as positive, negative and neutral 
    if mean >= 0.06 : 
        name = "positive" 
    
    elif mean <= - 0.06 : 
        name = "negative" 
	
    else : 
        name = "Neutral"
    return json.dumps(name)



if __name__ == "__main__":
    app.run(debug=True, port=5003)
