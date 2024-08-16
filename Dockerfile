FROM archlinux:latest
WORKDIR /code
ENV FLASK_RUN_HOST=0.0.0.0
ENV VIRTUAL_ENV=/opt/venv
ENV GOPATH=/go
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk
ENV PATH="$VIRTUAL_ENV/bin:$GOPATH/bin:$HOME/.sdkman/candidates/kotlin/current/bin:$JAVA_HOME/bin:$PATH"

RUN pacman -Sy --noconfirm && \
    pacman -Su --noconfirm python-pip git gcc gdb nodejs-lts-hydrogen npm unzip zip make lsof go curl dos2unix jdk11-openjdk && \
    curl -s https://get.sdkman.io | bash && \
    bash -c "source $HOME/.sdkman/bin/sdkman-init.sh && sdk install kotlin 1.9.22"

RUN python -m venv $VIRTUAL_ENV

COPY LiveFromDAP/requirements.txt requirements.txt
COPY LiveFromDAP/pyproject.toml pyproject.toml
RUN pip install -r requirements.txt
RUN pip install -e .

COPY LiveFromDAP/install.sh install.sh
RUN dos2unix install.sh install.sh
COPY LiveFromDAP/src/livefromdap/runner/. ./src/livefromdap/runner/
COPY LiveFromDAP/src/livefromdap/Makefile ./src/livefromdap/Makefile
RUN ./install.sh

COPY LiveFromDAP/. .
WORKDIR /code