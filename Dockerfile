FROM archlinux:latest
WORKDIR /code
ENV FLASK_RUN_HOST=0.0.0.0

RUN pacman -Sy
RUN pacman -Su --noconfirm python-pip git jdk-openjdk gcc gdb nodejs-lts-hydrogen npm unzip make lsof 

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY LiveFromDAP/requirements.txt requirements.txt
COPY LiveFromDAP/pyproject.toml pyproject.toml
RUN pip install -r requirements.txt
RUN pip install -e .

COPY LiveFromDAP/install.sh install.sh
COPY LiveFromDAP/src/livefromdap/runner/. ./src/livefromdap/runner/
COPY LiveFromDAP/src/livefromdap/Makefile ./src/livefromdap/Makefile
RUN ./install.sh

COPY LiveFromDAP/. .
WORKDIR /code
ENTRYPOINT [ "python", "src/main.py" ]