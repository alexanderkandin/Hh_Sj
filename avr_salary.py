
from itertools import count
from dotenv import load_dotenv

import os
import time
from terminaltables import AsciiTable
import requests


def display_salary_statistics(languages_info):
    table = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']
    ]
    for language, info in languages_info.items():
        table.append([
            language,
            info["vacancies_found"],
            info["vacancies_processed"],
            info["average_salary"]
        ])

    table_created = AsciiTable(table, 'HeadHunter Moscow')
    print(table_created.table)

def calc_avg_salary_sj():
    url = 'https://api.superjob.ru/2.0/vacancies/'
    load_dotenv()
    api_key = os.getenv('SJ_API_KEY')
    language_list = ['Python', 'Java', 'Javascript']
    languages_info = {}
    moscow_city = 4
    programmers_id = 48


    for language in language_list:
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
        total_vacancies = 0

        for page in count():
            params['page'] = page
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            vacancies = response.json().get('objects')
            if page == 0:
                total_vacancies = response.json().get('total', 0)

            if not vacancies:
                break

            for vacancy in vacancies:
                if vacancy.get('payment_from') is None and vacancy.get('payment_to'):
                    salaries.append(vacancy.get('payment_to') * 0.8)
                elif vacancy.get('payment_to') is None and vacancy.get('payment_from'):
                    salaries.append(vacancy.get('payment_from') * 1.2)
                elif vacancy.get('payment_to') and vacancy.get('payment_from'):
                    salaries.append((vacancy.get('payment_to') + vacancy.get('payment_from')) / 2)



        if salaries:
            salary_avr = sum(salaries) / len(salaries)
        else:
            salary_avr = 0

        languages_info[language] = {
            "vacancies_found": total_vacancies,
            "vacancies_processed": len(salaries),
            "average_salary": int(salary_avr)
        }
    display_salary_statistics(languages_info)


def calc_avg_salary_hh():
    url = 'https://api.hh.ru/vacancies'
    language_list = ['Python', 'Java', 'Javascript']
    languages_info = {}
    moscow_city = 1
    for language in language_list:
        payload = {
            "currency": "RUR",
            'text': language,
            'page': 0,
            "filter_exp_period": 30,
            'area': moscow_city

        }
        salaries = []
        total_vacancies = 0

        for page in count():
            payload['page'] = page
            response = requests.get(url, params=payload)

            if page >=100:
                break
            elif response.status_code == 403:
                time.sleep(60)
                continue

            response.raise_for_status()
            vacancies = response.json().get("items", [])
            total_vacancies = response.json().get("found", 0)

            if not vacancies:
                break

            total_vacancies += len(vacancies)

            for vacancy in vacancies:
                salary = vacancy.get("salary")
                if salary and salary.get("currency") == "RUR":
                    if salary.get('from') is None and salary.get('to'):
                        salaries.append(salary.get('to') * 0.8)
                    elif salary.get('to') is None and salary.get('from'):
                        salaries.append(salary.get('from') * 1.2)
                    elif salary.get('to') and salary.get('from'):
                        salaries.append((salary.get('to') + salary.get('from')) / 2)
                    else:
                        salaries.append(0)


        if salaries:
            salary_avr = sum(salaries) / len(salaries)
        else:
            salary_avr = 0

        languages_info[language] = {
            "vacancies_found": total_vacancies,
            "vacancies_processed": len(salaries),
            "average_salary": int(salary_avr)
        }
    display_salary_statistics(languages_info)


def main():
    calc_avg_salary_sj()
    calc_avg_salary_hh()

if __name__ == '__main__':
    main()