FROM python:3.8.20-slim AS pymol-build

# Install PyMOL Open Source and its requirements
RUN apt update  && apt install -y --no-install-recommends git build-essential libglew-dev libglm-dev libfreetype-dev libxml2-dev libxslt1-dev

WORKDIR /app

RUN python3.8 -m venv pymol-venv

COPY requirements-pymol.txt .
RUN pymol-venv/bin/pip install --no-cache-dir -r requirements-pymol.txt

RUN git clone https://github.com/schrodinger/pymol-open-source.git
RUN cd pymol-open-source && git checkout tags/v2.4.0 && /app/pymol-venv/bin/python3.8 setup.py install --no-vmd-plugins


FROM python:3.12.3-slim AS release

WORKDIR /app

RUN apt update && apt install -y --no-install-recommends build-essential wget libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev

RUN wget https://www.python.org/ftp/python/3.8.20/Python-3.8.20.tgz && tar -xzf Python-3.8.20.tgz && cd Python-3.8.20 && ./configure --enable-optimizations && make -j$(nproc) && make altinstall

COPY --from=pymol-build /app/pymol-venv /app/pymol-venv

RUN apt update && apt install -y --no-install-recommends libglew-dev libglm-dev libfreetype-dev sshpass rsync openssh-client

# Install Mono
RUN apt install -y --no-install-recommends dirmngr ca-certificates gnupg

RUN gpg --homedir /tmp --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/mono-official-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF

RUN chmod +r /usr/share/keyrings/mono-official-archive-keyring.gpg

RUN echo "deb [signed-by=/usr/share/keyrings/mono-official-archive-keyring.gpg] https://download.mono-project.com/repo/debian stable-buster main" > /etc/apt/sources.list.d/mono-official-stable.list

RUN apt install -y mono-complete

# Install MV and PQ
RUN apt install -y --no-install-recommends curl unzip && rm -rf /var/lib/apt/lists/*

RUN mkdir /app/mv /app/pq

RUN curl -L https://webchem.ncbr.muni.cz/Platform/MotiveValidator/DownloadService/1.1.23.12.27b -o MotiveValidator_1.1.23.12.27b.zip && unzip MotiveValidator_1.1.23.12.27b.zip -d /app/mv/MotiveValidator_1.1.23.12.27b && rm MotiveValidator_1.1.23.12.27b.zip

RUN curl -L https://webchem.ncbr.muni.cz/Platform/PatternQuery/DownloadService/1.1.23.12.27b -o PatternQuery_1.1.23.12.27b.zip && unzip PatternQuery_1.1.23.12.27b.zip -d /app/pq/PatternQuery_1.1.23.12.27b && rm PatternQuery_1.1.23.12.27b.zip


COPY ./src /app/src

CMD ["tail", "-f", "/dev/null"]
