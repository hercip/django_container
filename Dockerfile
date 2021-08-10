FROM python:3
LABEL maintainer="cip@ibit.ro"
# ARG CODE_LOCATION
ENV CODE_LOCATION=/opt/hc/django

ENV DEBIAN_FRONTEND=noninteractive
RUN \
  apt-get update && \
  apt-get install -y sudo curl git-core gnupg locales zsh \
  wget fonts-powerline && \
  locale-gen en_US.UTF-8
ENV DEBIAN_FRONTEND=dialog
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && /usr/sbin/locale-gen
ENV SHELL /bin/zsh
ADD . ${CODE_LOCATION}/
RUN \
  wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true && \
  git clone https://github.com/romkatv/powerlevel10k.git ~/.oh-my-zsh/custom/themes/powerlevel10k && \
  cd $HOME && curl -fsSLO https://raw.githubusercontent.com/romkatv/dotfiles-public/master/.purepower &&\
  pip install -r ${CODE_LOCATION}/code/requirements.dev.txt
ADD .devcontainer/.* /root/
WORKDIR ${CODE_LOCATION}/code/
ENV PYTHONUNBUFFERED 1
ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "./manage.py", "runserver", "0.0.0.0:8000"]
