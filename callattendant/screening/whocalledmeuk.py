#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
#  WhoCalledMeUK.py
#
#  Copyright 2021 Thomas BARDET <thomas.bardet@cloud-forge.net>
#  Copyright 2024 Ted Hess <thess@kitschensync.net>
#  Copyright 2024 RenOfHeavens (https://github.com/RenOfHeavens)

#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.


import requests
from bs4 import BeautifulSoup

class WhoCalledMeUK(object):

    def lookup_number(self, number):
        url = "https://who-called.co.uk/Number/{!s}".format(number)
        allowed_codes = [404]  # allow not found response
        content = self.http_get(url, allowed_codes)
        # Assuming not spam
        reason = ""
        score = 0

        soup = BeautifulSoup(content, "lxml")  # lxml HTML parser: fast 

        callStatsContainer = soup.find(class_="call-stats-item")
        if callStatsContainer is not None:

            reputationContainer = callStatsContainer.find(class_="Negative-Box")
            if reputationContainer is not None:
                score = 2

                numbers = soup.find(class_="panel-box-text")
                if len(numbers) > 0:
                    spanReason = numbers.select("mark")
                    reason = spanReason[0].get_text()
                    reason = reason.replace("\n", "").strip(" ")

        spam = False if score < self.spam_threshold else True

        return {"spam": spam, "score": score, "reason": reason}

    def http_get(self, url, allowed_codes=None):
        session = requests.Session()
        data = ""
        try:
            response = session.get(url, timeout=5)
            if response.status_code == 200:
                data = response.text
            elif response.status_code not in allowed_codes:
                response.raise_for_status()
        except requests.HTTPError as e:
            code = e.response.status_code
            print("HTTPError: {}".format(code))
            raise

        return data

    def __init__(self, spam_threshold=2):
        self.spam_threshold = spam_threshold
