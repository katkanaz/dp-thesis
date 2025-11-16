FROM python:3.8.20-slim AS pymol-build

# Install Python libraries, Pymol Open Source
RUN apt update  && apt install -y --no-install-recommends git build-essential libglew-dev libglm-dev libfreetype-dev libxml2-dev libxslt1-dev

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN git clone https://github.com/schrodinger/pymol-open-source.git
RUN cd pymol-open-source && git checkout tags/v2.4.0 && python setup.py install --no-vmd-plugins


FROM python:3.8.20-slim AS release

WORKDIR /app

COPY --from=pymol-build /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages

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
