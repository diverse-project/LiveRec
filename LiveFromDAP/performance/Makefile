
all : performance scenario

performance : execute_performance.csv general_performance.csv load_code_performance.csv

execute_performance.csv : execute_performance.py
	python execute_performance.py

general_performance.csv : general_performance.py
	python general_performance.py

load_code_performance.csv : load_code_performance.py
	python load_code_performance.py

scenario : scenario/binary_search_c_times.json scenario/binary_search_java_times.json scenario/binary_search_python_times.json

scenario/binary_search_c_times.json : scenario/evaluate_c.py
	cd scenario && python evaluate_c.py

scenario/binary_search_java_times.json : scenario/evaluate_java.py
	cd scenario && python evaluate_java.py

scenario/binary_search_python_times.json : scenario/evaluate_python.py
	cd scenario && python evaluate_python.py

scenario/binary_search_javascript_times.json : scenario/evaluate_javascript.py
	cd scenario && python evaluate_javascript.py

.PHONY : clean

clean :
	find . -name "*.csv" | grep -v jdi_times.csv | xargs rm
	rm -f scenario/*.json