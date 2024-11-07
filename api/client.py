import requests
from time import sleep
from datetime import datetime
import pandas as pd
import os
from categorization.categorize_data import categorize_transactions

class DKBapi:
    def __init__(self,account_name='Girokonto',device_name='DKB-App auf iPhone'):

        self.device_name = device_name

        data_file = f'DKB_transactions_{account_name}.xlsx'
        # check if data file exists
        if os.path.isfile(data_file):
            self.transaction_data = pd.read_excel(data_file)
        else:
            self.transaction_data = pd.DataFrame(columns=['bookingDate','description','currencyCode','value','creditorName','deptorName','category', "currentBalance"])
            self.transaction_data.to_excel(data_file)

        self.base_url = 'https://banking.dkb.de/'

        # create session
        self.session = requests.Session()

    def login(self, username, password):
        # get csrf token
        self.session.get(self.base_url + 'login')
        self.csrf_token = self.session.cookies.get('__Host-xsrf')


        # login
        token_response = self.session.post(
            self.base_url + 'api/token',
            data={
                'username': username,
                'password': password,
                'grant_type': 'banking_user_sca',
                'sca_type': 'web-login'
            },
            headers = {
                'X-Xsrf-Token': self.csrf_token,
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        if token_response.status_code != 200:
            return {'message': 'Login failed'}

        self.mfa_id = token_response.json()['mfa_id']
        self.access_token = token_response.json()['access_token']

        # 2-factor authentication
        print('2 Factor Authentication', end="\r")
        mfa_response = self.session.get(
            self.base_url + f'api/mfa/mfa/{self.mfa_id}/methods',
            headers={'Accept': 'application/vnd.api+json',
                     'X-Xsrf-Token': self.csrf_token
                     },
            params={
                'filter%5BmethodType%5D': 'seal_one',
                'filter%5BmethodType%5D': 'chip_tan_qr',
                'filter%5BmethodType%5D': 'chip_tan_manual',
            }
            # params={
            #     'filter[methodType]': 'seal_one',
            #     'filter[methodType]': 'chip_tan_qr',
            #     'filter[methodType]': 'chip_tan_manual',
            # }
        )

        for data in mfa_response.json()['data']:
            if data['attributes']['deviceName'] == self.device_name:
                methodId = data['id']
                methodType = data['attributes']['methodType']


        mfa_challenge_response = self.session.post(
            self.base_url + 'api/mfa/mfa/challenges',
            headers={
                'Accept': 'application/vnd.api+json',
                'X-Xsrf-Token': self.csrf_token,
                'Content-Type': 'application/vnd.api+json'
            },
            json={
                "data":
                    {
                        "type":"mfa-challenge",
                        "attributes":
                            {
                                "mfaId":self.mfa_id,
                                "methodId": methodId,
                                "methodType": methodType
                            }
                    }
            }
        )

        self.mfa_challenge_id = mfa_challenge_response.json()['data']['id']

        return {'message': 'Login successful'}

    def check_mfa_status(self):
        mfa_challenge_response2 = self.session.get(
            self.base_url + f'api/mfa/mfa/challenges/{self.mfa_challenge_id}',
            headers={'Accept': 'application/vnd.api+json',
                        'X-Xsrf-Token': self.csrf_token
                     }
        )

        if mfa_challenge_response2.json()['data']['attributes']['verificationStatus'] == 'processed':
            self.session.post(
                self.base_url + 'api/token',
                data={
                    'grant_type': 'banking_user_mfa',
                    'mfa_id': self.mfa_id,
                    'access_token': self.access_token,
                },
                headers={
                    'X-Xsrf-Token': self.csrf_token,
                    'Accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )
        # return processing or processed
        return mfa_challenge_response2.json()['data']['attributes']['verificationStatus']

    def wait_for_mfa(self, check_interval=5, timeout=120):
        counter = 1
        while counter * check_interval <= timeout:
            counter += 1
            timer_counter = 0
            while timer_counter < check_interval:
                print('2 Factor Authentication .' + int(timer_counter % 3) * '.', end="\r")
                timer_counter += 0.3
                sleep(0.3)
            status = self.check_mfa_status()
            if status == 'processed':
                print('2 Factor Authentication ... done!')
                return True
        return False

    def get_account_id(self,account_name='Girokonto'):
        self.account_name = account_name
        # get account id
        accounts_response = self.session.get(
            self.base_url + 'api/accounts/accounts',
            headers={'Accept': 'application/json, text/plain, */*',
                     'X-Xsrf-Token': self.csrf_token
                     }
        )

        for data in accounts_response.json()['data']:
            if data['attributes']['product']['displayName'] == account_name:
                account_id = data['id']
                self.current_balance = data['attributes']['nearTimeBalance']['value']
        return account_id

    def get_transactions(self,
                         account_id,
                         page_size=25,
                         from_date=datetime.now().replace(year=datetime.now().year - 1).strftime('%Y-%m-%d'),
                         to_date=datetime.now().strftime('%Y-%m-%d'),
                         save=True
                         ):

        if not self.transaction_data.empty and datetime.strptime(self.transaction_data.values[0][0], '%Y-%m-%d') > datetime.strptime(from_date, '%Y-%m-%d'):
            from_date = self.transaction_data.values[0][0]

        # get transactions
        transaction_response = self.session.get(
            self.base_url + f'api/accounts/accounts/{account_id}/transactions',
            headers={'Accept': 'application/json, text/plain, */*',
                     'X-Xsrf-Token': self.csrf_token
                     }
            ,
            params={'filter[bookingDate][GE]': from_date,
                    'filter[bookingDate][LE]': to_date,
                    'page%5Bsize%5D': page_size,
                    'expand': 'Merchant',
                    }
        )

        transactions = transaction_response.json()['data']

        transaction_data = [
            {
                "bookingDate": item["attributes"]["bookingDate"],
                "description": item["attributes"]["description"] if "description" in item["attributes"] else "",
                "currencyCode": item["attributes"]["amount"]["currencyCode"],
                "value": item["attributes"]["amount"]["value"],
                "creditorName": item["attributes"]["creditor"]["name"],
                "deptorName": item["attributes"]["debtor"]["name"] if "debtor" in item["attributes"] else "",
                "currentBalance": self.current_balance
            }
            for item in transactions]

        new_transaction_data = pd.DataFrame(
            transaction_data,
            columns=["bookingDate", "description", "currencyCode", "value", "creditorName","deptorName", "currentBalance"])

        new_transaction_data_with_categories = categorize_transactions(new_transaction_data)

        if save:
            # Concatenate existing and new data
            updated_transaction_data = pd.concat([new_transaction_data_with_categories,self.transaction_data])

            # Drop duplicates based on columns that define unique transactions
            updated_transaction_data = updated_transaction_data.drop_duplicates(subset=["bookingDate", "description", "currencyCode", "value"])

            updated_transaction_data.to_excel(f'DKB_transactions_{self.account_name}.xlsx', index=False)

            return updated_transaction_data
        else:
            return new_transaction_data_with_categories

    def update_bank_data(self,account_name='Girokonto',page_size=100):

        account_id = self.get_account_id(account_name=account_name)

        transactions = self.get_transactions(account_id=account_id,page_size=page_size)

        return transactions
