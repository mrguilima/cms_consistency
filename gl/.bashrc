
alias di='ls -FlAtor'
alias up='cd ..'
alias rse='grep \: /consistency/config.yaml | grep T | cut -d: -f1 | cut -c3- | grep'
alias glog='git log --all --graph --pretty=format:"%C(yellow)%h %C(green)%ar %C(bold cyan)%an%C(magenta)%d%C(reset) %s"'

export PS1='\n\[\e[1;33m\]== \W ==>>>\[\e[0m\] '
export X509_USER_PROXY=/tmp/x509up
#export XRD_LOGDLEVEL=clear  #Error  #Debug

cd /consistency/cms_consistency/site_cmp3

