
#.. take RSE from argument (default RSE=UERJ)
RSE=T2_BR_UERJ
test -z $1 || RSE=$1

scope=cms
python=${PYTHON:-python}
export PYTHONPATH=/consistency/cms_consistency/site_cmp3:/consistency/cms_consistency/cmp3

python=/usr/bin/python3.9
out=/var/cache/test
dump=/var/cache/consistency-dump

now=`date -u +%Y_%m_%d_%H_%M`
lastRun=`ls -1 ${dump}/${RSE}*config.yaml | tail -1 | cut -c29- | sed 's#_config.yaml##'`
echo lastRun=$lastRun

merged_config_file=${dump}/${lastRun}_config.yaml
stats=${out}/${RSE}_${now}_stats.json

# 5. Declare missing and dark replicas
#    -d turns it into "dry run" mode
echo merged_config_file=${merged_config_file}
missing_action_errors=${out}/${RSE}_${now}_missing_action.errors
m_action_list=${out}/${RSE}_${now}_M_action.list
echo ====
echo
echo Missing files ...
echo
$python actions/declare_missing.py -d -a root -o ${m_action_list} -c ${merged_config_file} -s $stats $out $scope $RSE 2>> ${missing_action_errors}
