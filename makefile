run:
	uvicorn src.main:app --reload --host 0.0.0.0

generate_requirements_txt:
	pipenv requirements --dev  > requirements.txt

test:
	rm -f test.db
	db_path="test.db" pytest -x -vv

install:
	pipenv install --dev
