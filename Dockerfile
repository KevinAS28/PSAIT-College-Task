# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.134.1/containers/python-3/.devcontainer/base.Dockerfile
ARG VARIANT="3"
# FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}
FROM python:3.9-bullseye

WORKDIR /app

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
COPY requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp


# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update \
#     && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

EXPOSE 9999

COPY . .
# CMD ["python", "manage.py", "runserver", "0.0.0.0:9999"]
# RUN python manage.py runserver 0.0.0.0:9999