
from itertools import count
from dotenv import load_dotenv

import os
import time
from terminaltables import AsciiTable
import requests


def calculate_salary(min_salary, max_salary, currency=None, target_currency=None):

    payment_from = min_salary
    payment_to = max_salary

    if currency != target_currency:
        return None

    if payment_from is None and payment_to:
        return payment_to * 0.8
    elif payment_to is None and payment_from:
        return payment_from * 1.2
    elif payment_from and payment_to:
        return (payment_from + payment_to) / 2


def display_salary_statistics(languages_statistic):
    table = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']
    ]
    for language, info in languages_statistic.items():
        table.append([
            language,
            info["vacancies_found"],
            info["found_vacancies"],
            info["average_salary"]
        ])

    table_created = AsciiTable(table, 'HeadHunter Moscow')
    print(table_created.table)

def calc_avg_salary_sj(api_key):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    languages = ['Python', 'Java', 'Javascript']
    languages_statistic = {}
    moscow_city = 4
    programmers_id = 48


    for language in languages:
        params = {
            'keyword' : language,
            'town' : moscow_city,
            'catalogues': programmers_id,
            'currency' : 'rub',
            'page' : 0
        }

        headers ={
            'X-Api-App-Id' : api_key
        }

        salaries = []

        for page in count():
            params['page'] = page
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            vacancy_details = response.json()
            vacancies = vacancy_details.get('objects')
            if page == 0:
                total_vacancies = vacancy_details.get('total', 0)

            if not vacancies:
                break

            for vacancy in vacancies:
                min_salary = vacancy.get('payment_from')
                max_salary = vacancy.get("payment_to")
                salary = calculate_salary(min_salary, max_salary)
                if salary:
                    salaries.append(salary)


        if salaries:
            salary_avr = sum(salaries) / len(salaries)
        else:
            salary_avr = 0

        languages_statistic[language] = {
            "vacancies_found": total_vacancies,
            "found_vacancies": len(salaries),
            "average_salary": int(salary_avr)
        }
    display_salary_statistics(languages_statistic)


def calc_avg_salary_hh():
    url = 'https://api.hh.ru/vacancies'
    languages = ['Python', 'Java', 'Javascript']
    languages_statistic = {}
    moscow_city = 1
    for language in languages:
        payload = {
            "currency": "RUR",
            'text': language,
            'page': 0,
            "filter_exp_period": 30,
            'area': moscow_city

        }
        salaries = []

        for page in count():
            payload['page'] = page
            response = requests.get(url, params=payload)

            if page >=100:
                break
            elif response.status_code == 403:
                time.sleep(60)
                continue

            response.raise_for_status()
            vacancy_details = response.json()
            vacancies = vacancy_details.get("items", [])
            total_vacancies = vacancy_details.get("found", 0)

            if not vacancies:
                break


            for vacancy in vacancies:

                currency = vacancy.get('currency')
                min_salary = vacancy.get('from')
                max_salary = vacancy.get("to")

                salary = calculate_salary(min_salary, max_salary, currency, "RUR")
                if salary:
                    salaries.append(salary)

        if salaries:
            salary_avr = sum(salaries) / len(salaries)
        else:
            salary_avr = 0

        languages_statistic[language] = {
            "vacancies_found": total_vacancies,
            "found_vacancies": len(salaries),
            "average_salary": int(salary_avr)
        }
    display_salary_statistics(languages_statistic)


def main():
    load_dotenv()
    api_key = os.getenv('SJ_API_KEY')
    calc_avg_salary_sj(api_key)
    calc_avg_salary_hh()

if __name__ == '__main__':
    main()