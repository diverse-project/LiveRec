FROM archlinux:latest
WORKDIR /code
ENV FLASK_RUN_HOST=0.0.0.0
COPY LiveFromDAP/. .
RUN pacman -Sy
RUN pacman -S --noconfirm python-pip git jdk-openjdk gcc gdb nodejs-lts-hydrogen npm unzip make

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -r requirements.txt
RUN pip install -e .
RUN ./install.sh

CMD [ "flask", "-A", "/code/src/webdemo/main:app", "run" ]