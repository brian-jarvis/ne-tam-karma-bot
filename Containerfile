FROM registry.redhat.io/ubi8/ubi-minimal:8.5

LABEL org.opencontainers.image.authors="bry@redhat.com"

RUN microdnf  install  python39 python39-six python39-requests && microdnf clean all

LABEL version="8.5"
LABEL summary="A containerized IRC Bot for Ne TAMs."
LABEL description="The KarmaBot allows giving karma to everyone in a channel."
LABEL AppCode=TAMT-001
LABEL paas.redhat.com/appcode=TAMT-001

COPY ./ /opt/KarmaBot

ENTRYPOINT [ "python3", "/opt/KarmaBot/ircbot.py" ]
