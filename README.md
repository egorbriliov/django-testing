# Django Testing: YaNote & YaNews

![Python](https://img.shields.io/badge/python-black?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-black.svg?style=for-the-badge&logo=django&logoColor=3CB371)
![pytest](https://img.shields.io/badge/pytest-black.svg?style=for-the-badge&logo=pytest&logoColor=white)
![unittest](https://img.shields.io/badge/unittest-black.svg?style=for-the-badge&logo=labex&logoColor=6A5ACD)

## Description

This project was developed as part of the **Yandex Practicum** curriculum. The main goal was to master Django application testing using various frameworks and methodologies.

The repository includes two separate applications:

1. **YaNote** — a note-taking service tested with the standard **Unittest** library.

2. **YaNews** — a news portal tested with the **Pytest** framework.

## Purpose

This project serves as a showcase of my Backend QA skills. It demonstrates my ability to write maintainable tests, manage fixtures, and verify complex business logic within real-world Django environments.

## Key Testing Areas

- **Models:** Ensuring correct object creation, string representations, and attribute validation.
- **URLs & Access:** Verifying page availability for anonymous users, authorized users, and content authors.
- **Forms:** Data validation and handling of edge cases in user input.
- **Business Logic:** Testing CRUD operations (Create, Read, Update, Delete) for notes and comments.

## Setup & Installation

###

#### 1. Clone the repository

```bash
git clone https://github.com
cd django_testing
```

#### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

#### 3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

#### 4. Run tests

For **YaNote** (Unittest):

```bash
python manage.py test yanote
```

For **YaNews** (Pytest):

```bash
pytest
```

## Contacts

[![Telegram](https://shields.io)](https://t.me)
[![LinkedIn](https://shields.io)](https://linkedin.com)
