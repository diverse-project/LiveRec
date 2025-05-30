FROM archlinux:latest
WORKDIR /code
ENV FLASK_RUN_HOST=0.0.0.0

RUN pacman -Sy --noconfirm
RUN pacman -Su --noconfirm python-pip git jdk-openjdk gcc gdb nodejs npm unzip make lsof go

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV GOPATH=/go
ENV PATH="$GOPATH/bin:$PATH"

COPY LiveFromDAP/requirements.txt requirements.txt
COPY LiveFromDAP/pyproject.toml pyproject.toml
RUN pip install -r requirements.txt
RUN pip install -e .

COPY LiveFromDAP/src/livefromdap/runner/. ./src/livefromdap/runner/
COPY LiveFromDAP/src/livefromdap/Makefile ./src/livefromdap/Makefile
COPY LiveFromDAP/install.sh install.sh
RUN ./install.sh

COPY PolyDebug/PolyDebug/src/polydebug/runner/. ./PolyDebug/src/polydebug/runner/
COPY PolyDebug/PolyDebug/src/polydebug/Makefile ./PolyDebug/src/polydebug/Makefile
COPY PolyDebug/PolyDebug/install.sh ./PolyDebug/install.sh
WORKDIR /code/PolyDebug
RUN ./install.sh
WORKDIR /code

COPY PolyDebug/PolyDebug /code/PolyDebug
COPY LiveFromDAP/. .
COPY test.py /test/foobar.py
COPY test.js /test/square.js
WORKDIR /code
ENTRYPOINT [ "flask", "-A", "src/webdemo/main.py:app", "run" ]