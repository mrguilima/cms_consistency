
RSE=$1
config_file=/var/cache/test/config.yaml
merged_config_file=/var/cache/test/merged.out
python=${PYTHON:-python}
export PYTHONPATH=/consistency/cms_consistency/site_cmp3:/consistency/cms_consistency/cmp3

#python=/usr/bin/python3.9

$python merge_config.py merge $RSE $config_file > $merged_config_file

disabled=`$python merge_config.py get -d false $merged_config_file rses.$RSE.ce_disabled`
case $disabled in
  True|true)
    disabled="true"
    ;;
  False|false)
    disabled="false"
    ;;
  *)
    disabled="false"
    ;;
esac

echo "RSE disabled:           $disabled"
