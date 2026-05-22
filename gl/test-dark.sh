
#RSE=T3_US_Colorado
RSE=T1_DE_KIT_Tape
now=`date -u +%Y_%m_%d_%H_%M`

dump=/var/cache/consistency-dump
last=2`ls -1 ${dump}/${RSE}*config.yaml | tail -1 | cut -d'_' -f2- | cut -d2 -f2- | cut -dc -f1`
echo RSE=${RSE}
echo now=${now}
echo last=${last}

echo
echo Testing dark_action ...
echo
python=`which python3`
export PYTHONPATH=/consistency/cms_consistency/site_cmp3:/consistency/cms_consistency/site_cmp3/cmp3

out=/var/cache/test
dark_list=${out}/test-${RSE}_${now}_D_action.list.gz
dark_errors=${out}/test-${RSE}_${now}_dark_action.errors

$python /consistency/cms_consistency/actions/declare_dark_GL.py \
	-a root \
	-o ${dark_list} \
	-c ${dump}/${RSE}_${last}config.yaml \
	-s ${out}/test-${RSE}_${now}_stats.json \
	${dump} ${RSE} \
	2>> ${dark_errors}

