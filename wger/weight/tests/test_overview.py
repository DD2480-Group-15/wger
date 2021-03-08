# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Standard Library
import logging
import sys
import os
o_path = os.getcwd()
sys.path.append(o_path)
# Django
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.urls import reverse

# wger
from wger.weight.models import WeightEntry

from wger.core.demo import create_demo_entries

from wger.core.tests.base_testcase import WgerTestCase


logger = logging.getLogger(__name__)


class WeightOverviewTestCase(WgerTestCase):
    """
    Test case for the weight overview page
    """

    def weight_overview(self):
        """
        Helper function to test the weight overview page
        """
        response = self.client.get(reverse('weight:overview',
                                           kwargs={'username': self.current_user}))
        self.assertEqual(response.status_code, 200)

    def test_weight_overview_loged_in(self):
        """
        Test the weight overview page by a logged in user
        """
        self.user_login('test')
        self.weight_overview()

    def test_calorie(self):
        username='my_test'
        password='123456QWERT'
        email = ''
        user = User.objects.create_user(username, email, password)
        user.save()
        user_profile = user.userprofile
        user_profile.is_temporary = False
        user_profile.age = 25
        user_profile.height = 175
        user_profile.save()
        user = authenticate(username=username, password=password)
        create_demo_entries(user=user)
        self.user_login('my_test')
        response = self.client.get(reverse('weight:overview',
                                           kwargs={'username': self.current_user}))
        from lxml import etree
        dom = etree.HTML(str(response.content))
        date = dom.xpath(
            '/html/body/div/div//div[@id="content"]//table[@class="table"]/tr//td[1]/text()')
        plan_c = dom.xpath(
            '/html/body/div/div//div[@id="content"]//table[@class="table"]/tr//td[5]/text()')
        log_c = dom.xpath(
            '/html/body/div/div//div[@id="content"]//table[@class="table"]/tr//td[6]/text()')
        import json
        f = open('./wger/weight/fixtures/test_calorie_data.json')
        data = json.load(f)
        for i in range(len(date)):
            self.assertEqual(plan_c[i], str(data[i]['Planned Calorie/Kcal']))
            self.assertEqual(log_c[i], str(data[i]['Logged Calorie/Kcal']))

class WeightExportCsvTestCase(WgerTestCase):
    """
    Tests exporting the saved weight entries as a CSV file
    """

    def csv_export(self):
        """
        Helper function to test exporting the saved weight entries as a CSV file
        """
        response = self.client.get(reverse('weight:export-csv'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertGreaterEqual(len(response.content), 120)
        self.assertLessEqual(len(response.content), 150)

    def test_csv_export_loged_in(self):
        """
        Test exporting the saved weight entries as a CSV file by a logged in user
        """
        self.user_login('test')
        self.csv_export()
