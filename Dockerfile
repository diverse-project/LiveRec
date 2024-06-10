FROM archlinux:latest
WORKDIR /code
ENV FLASK_RUN_HOST=0.0.0.0

RUN pacman -Sy --noconfirm && \
    pacman -Su --noconfirm && \
    pacman -S --noconfirm python-pip git jdk-openjdk gcc gdb nodejs-lts-hydrogen npm unzip make lsof go

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV GOPATH=/go
ENV PATH="$GOPATH/bin:$PATH"

COPY LiveFromDAP/requirements.txt requirements.txt
COPY LiveFromDAP/pyproject.toml pyproject.toml
RUN pip install -r requirements.txt
RUN pip install -e .

COPY LiveFromDAP/install.sh install.sh
RUN pacman -Syu --noconfirm dos2unix
RUN dos2unix install.sh install.sh
COPY LiveFromDAP/src/livefromdap/runner/. ./src/livefromdap/runner/
COPY LiveFromDAP/src/livefromdap/Makefile ./src/livefromdap/Makefile
RUN ./install.sh

COPY LiveFromDAP/. .
WORKDIR /code